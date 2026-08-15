"""
chatbot.py
----------
Lõi xử lý RAG Chatbot Công an xã An Viễn theo kiến trúc "Hybrid Adaptive Correct RAG":
1. Query Analyzer & Multi-Step Reasoning Chain (Phân tích & Tách ý định)
2. Vector DB Context + Graph DB Context Retrieval
3. Grader (Đánh giá độ phù hợp PASS / FAIL)
4. Web Search Fallback (Nếu Grader trả về FAIL hoặc CSDL không đủ)
5. LLM Synthesis Generation (Sinh câu trả lời chuẩn hành chính Công an xã An Viễn)
"""

import os
import sys

# -----------------------------------------------------------------------------
# CẤU HÌNH GEMINI API KEY: Điền API key của bạn vào dấu ngoặc kép dưới đây
# -----------------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

try:
    from google import genai
except ImportError:
    genai = None

def get_genai_client():
    api_key = os.environ.get("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None

def analyze_query(query: str) -> list[str]:
    """
    Query Analyzer & Reasoning Chain:
    Chuẩn hóa chính tả, tách câu hỏi chứa nhiều ý định (multi-intent) thành các sub-queries.
    """
    client = get_genai_client()
    if not client:
        return [query]

    prompt = f"""Bạn là một chuyên gia Phân tích Câu hỏi (Query Analyzer) của hệ thống RAG Chatbot Công an xã An Viễn, thành phố Đồng Nai.
Nhiệm vụ:
1. Đọc câu hỏi gốc của người dân.
2. Chuẩn hóa chính tả, từ viết tắt, tiếng lóng thành thuật ngữ hành chính công an (VD: "nhập khẩu" -> "đăng ký thường trú", "bán xe" -> "thu hồi đăng ký xe").
3. Nếu câu hỏi chứa NHIỀU thủ tục/vấn đề khác nhau (VD: vừa hỏi tạm trú vừa hỏi nộp phạt PCCC vừa hỏi số trực ban), hãy TÁCH thành các câu hỏi con độc lập.
4. Trả về kết quả dưới dạng danh sách, mỗi câu hỏi con trên 1 dòng. Không thêm ký tự thừa, không giải thích.

Câu hỏi gốc: "{query}"
Danh sách câu hỏi con chuẩn hóa:
"""
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt
        )
        lines = [line.strip('-*• ').strip() for line in response.text.strip().split('\n') if line.strip()]
        return lines if lines else [query]
    except Exception:
        return [query]

def check_context_relevance(query: str, context: str) -> bool:
    """
    Grader Node: Đánh giá xem Context (Vector DB + Graph DB) có chứa đủ thông tin để trả lời hay không.
    Trả về True (PASS) hoặc False (FAIL -> Cần Web Search).
    """
    if not context or len(context.strip()) < 50:
        return False

    client = get_genai_client()
    if not client:
        # Nếu không có API Key, đánh giá dựa trên độ dài context
        return len(context) > 100

    prompt = f"""Bạn là Chuyên gia Đánh giá Tài liệu (Grader).
Nhiệm vụ: Kiểm tra xem TÀI LIỆU CSDL có chứa đủ thông tin liên quan để trả lời CÂU HỎI của người dân hay không.

TÀI LIỆU CSDL:
{context[:3000]}

CÂU HỎI: "{query}"

Nếu TÀI LIỆU có chứa thông tin để trả lời (kể cả trả lời được 1 phần), hãy trả về: YES
Nếu TÀI LIỆU hoàn toàn không liên quan hoặc thiếu thông tin cốt lõi, hãy trả về: NO
Chỉ xuất đúng 1 từ YES hoặc NO.
"""
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt
        )
        ans = response.text.strip().upper()
        return "YES" in ans
    except Exception:
        return True

def get_llm_response(query: str, context: str, need_web_search: bool = False) -> str:
    """
    LLM Generator: Tổng hợp câu trả lời chuẩn văn phong hành chính CAND Công an xã An Viễn.
    """
    client = get_genai_client()
    if not client:
        return (
            "LỖI: Chưa thiết lập GEMINI_API_KEY.\n"
            "Vui lòng thiết lập biến môi trường GEMINI_API_KEY để sử dụng LLM Generation."
        )

    system_persona = """Bạn là Cán bộ tiếp nhận và trả lời Hướng dẫn Thủ tục Hành chính của CÔNG AN XÃ AN VIỄN, THÀNH PHỐ ĐỒNG NAI.

Quy tắc trả lời BẮT BUỘC:
1. Trả lời bằng tiếng Việt, xưng "Công an xã An Viễn" hoặc "Chúng tôi" và gọi người dân là "Anh/chị" hoặc "Bà con".
2. Văn phong chuẩn mực, nghiêm túc, lịch sự, chính xác theo quy định pháp luật và quy trình nghiệp vụ hành chính công sản xuất.
3. TUYỆT ĐỐI KHÔNG SỬ DỤNG BẤT KỲ EMOJI (biểu tượng cảm xúc), icon hay từ ngữ xì-tin, không dùng thuật ngữ AI hay Chatbot trong câu trả lời.
4. Trình bày rõ ràng bằng tiêu đề và gạch đầu dòng: Đối tượng áp dụng -> Thành phần hồ sơ -> Trình tự các bước thực hiện -> Thời hạn giải quyết & Lệ phí -> Thông tin cán bộ/bộ phận tiếp nhận.
5. Trường hợp vụ việc an ninh trật tự hoặc báo cháy khẩn cấp, luôn ghi rõ Số điện thoại Trực ban Công an xã An Viễn: 02513.538.187 hoặc các số khẩn cấp (113, 114, 115).
"""

    prompt = f"""{system_persona}

=== TÀI LIỆU TRÍ THỨC CSDL (VECTOR DB + GRAPH CONTEXT) ===
{context}
======================================================

Câu hỏi của người dân: "{query}"

Hãy soạn câu trả lời đầy đủ, chi tiết, dễ hiểu và chuẩn xác nhất cho người dân:
"""

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Rất tiếc, hệ thống gặp sự cố khi tổng hợp phản hồi: {str(e)}"
