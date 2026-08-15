"""
streamlit_app.py
----------------
Cổng Thông Tin Hướng Dẫn Thủ Tục Hành Chính - Công An Xã An Viễn
Tích hợp các tính năng nâng cao:
1. Bộ lọc tra cứu Cán bộ Công an phụ trách theo từng Ấp
2. Thanh bên Tải Mẫu đơn Hành chính Công (CT01, CT07, MĐ01, PC01)
3. Tải / In Phiếu Hướng dẫn Thủ tục Hành chính chính thức (Format văn bản hành chính)
"""

import os
import sys
import time
from datetime import datetime
import streamlit as st

# Thiết lập API Key từ Streamlit Secrets hoặc Môi trường
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

from chatbot import analyze_query, check_context_relevance, get_llm_response
from query import answer_query
from graph_index import get_graph_index

# Cấu hình Trang Streamlit
st.set_page_config(
    page_title="Cổng Thông Tin Hướng Dẫn Thủ Tục Hành Chính - Công An Xã An Viễn",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS giao diện Xanh Navy Công an Nhân dân chuẩn mực (Không emoji/AI)
st.markdown("""
<style>
    .main-header {
        background-color: #0b5394;
        color: #ffffff;
        padding: 20px 24px;
        border-radius: 8px;
        border-bottom: 3px solid #073863;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 1.35rem;
        font-weight: 700;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .main-header p {
        color: #cbd5e1;
        font-size: 0.9rem;
        margin: 4px 0 0 0;
    }
    .welcome-box {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #0b5394;
        padding: 16px 20px;
        border-radius: 6px;
        margin-bottom: 20px;
        color: #1e293b;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .officer-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 3px solid #0b5394;
        padding: 10px 14px;
        border-radius: 4px;
        margin-bottom: 8px;
        font-size: 0.85rem;
    }
    .stButton>button {
        background-color: #f1f5f9;
        color: #0b5394;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 500;
        padding: 6px 14px;
        width: 100%;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #0b5394;
        color: #ffffff;
        border-color: #0b5394;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# THANH BÊN (SIDEBAR) - TÍNH NĂNG NÂNG CAO
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏛️ CÔNG AN XÃ AN VIỄN")
    st.markdown("**Trực ban 24/24:** `02513.538.187`")
    st.divider()

    # 1. BỘ LỌC TRA CỨU CÁN BỘ PHỤ TRÁCH THEO ẤP
    st.markdown("### 👤 Cán Bộ Phụ Trách Theo Địa Bàn")
    selected_ap = st.selectbox(
        "Chọn địa bàn Ấp để tra cứu:",
        ["Tất cả địa bàn", "Ấp An Phú", "Ấp Phát Đạt", "Ấp Hưng Thịnh"]
    )

    graph = get_graph_index()
    all_contacts = graph.contacts

    filtered_contacts = all_contacts
    if selected_ap != "Tất cả địa bàn":
        filtered_contacts = [
            c for c in all_contacts 
            if selected_ap.lower() in c.get("role", "").lower() or selected_ap.lower() in c.get("title", "").lower() or selected_ap.lower() in c.get("area", "").lower()
        ]

    for c in filtered_contacts[:4]:
        st.markdown(f"""
        <div class="officer-card">
            <strong>{c['title']} - {c['name']}</strong><br/>
            <span>SĐT: <strong>{c['phone']}</strong></span><br/>
            <span style="color: #64748b; font-size: 0.8rem;">Phụ trách: {c['role']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 2. DANH SÁCH MẪU ĐƠN HÀNH CHÍNH
    st.markdown("### 📄 Tải Mẫu Đơn Hành Chính")
    
    st.markdown("**Mẫu CT01 - Tờ khai Cư trú**")
    st.caption("Tờ khai thay đổi thông tin cư trú (Đăng ký thường trú, tạm trú)")
    ct01_text = """CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n\nTỜ KHAI THAY ĐỔI THÔNG TIN CƯ TRÚ (Mẫu CT01)\nKính gửi: Công an xã An Viễn, thành phố Đồng Nai\n\n1. Họ và tên: ........................................................\n2. Ngày, tháng, năm sinh: ....../....../............ Sex: ..........\n3. Số định danh cá nhân/CCCD: .......................................\n4. Số điện thoại liên hệ: .............................................\n5. Nơi thường trú hiện tại: ...........................................\n6. Nơi tạm trú/Nơi ở hiện tại: ........................................\n7. Nội dung đề nghị: .................................................\n(Ví dụ: Đăng ký thường trú / Đăng ký tạm trú / Khai báo tạm vắng)\n\nAn Viễn, ngày ...... tháng ...... năm 202...\nNgười kê khai (Ký, ghi rõ họ tên)"""
    st.download_button("Tải Mẫu CT01 (.txt)", data=ct01_text, file_name="Mau_CT01_To_Khai_Cu_Tru.txt", mime="text/plain")

    st.markdown("**Mẫu CT07 - Giấy Xác Nhận Cư Trú**")
    st.caption("Đơn xin cấp xác nhận thông tin về cư trú")
    ct07_text = """CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n\nĐƠN XIN CẤP GIẤY XÁC NHẬN THÔNG TIN VỀ CƯ TRÚ (Mẫu CT07)\nKính gửi: Công an xã An Viễn, thành phố Đồng Nai\n\nTôi tên là: ...........................................................\nSố CCCD: .......................... Ngày cấp: .......... Nơi cấp: .......\nĐịa chỉ thường trú: ....................................................\nYêu cầu cấp Giấy xác nhận thông tin về cư trú để làm thủ tục: .........\n\nAn Viễn, ngày ...... tháng ...... năm 202...\nNgười làm đơn"""
    st.download_button("Tải Mẫu CT07 (.txt)", data=ct07_text, file_name="Mau_CT07_Xac_Nhan_Cu_Tru.txt", mime="text/plain")

    st.markdown("**Mẫu MĐ01 - Khai Đăng Ký Xe**")
    st.caption("Giấy khai đăng ký xe máy, ô tô")
    md01_text = """CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n\nGIẤY KHAI ĐĂNG KÝ XE (Mẫu MĐ01)\nKính gửi: Công an xã An Viễn, thành phố Đồng Nai\n\nTên chủ xe: ...........................................................\nĐịa chỉ: ..............................................................\nSố CCCD: .............................................................\nNhãn hiệu xe: ................ Loại xe: .......... Màu sơn: ...........\nSố khung: .............................................................\nSố máy: ...............................................................\nLý do: (Đăng ký mới / Sang tên / Cấp lại biển số)\n\nAn Viễn, ngày ...... tháng ...... năm 202...\nChủ xe (Ký, ghi rõ họ tên)"""
    st.download_button("Tải Mẫu MĐ01 (.txt)", data=md01_text, file_name="Mau_MD01_Dang_Ky_Xe.txt", mime="text/plain")

# -----------------------------------------------------------------------------
# PHẦN CHÍNH (MAIN CONTAINER)
# -----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>CỔNG THÔNG TIN HƯỚNG DẪN THỦ TỤC HÀNH CHÍNH - CÔNG AN XÃ AN VIỄN</h1>
    <p>Thành phố Đồng Nai | Trực ban Công an xã: 02513.538.187</p>
</div>
""", unsafe_allow_html=True)

# Khởi tạo Lịch sử Trò chuyện
if "messages" not in st.session_state:
    st.session_state.messages = []

# Thông điệp Chào mừng ban đầu nếu lịch sử trống
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="welcome-box">
        <p><strong>Kính chào Anh/chị và Bà con nhân dân xã An Viễn!</strong></p>
        <p>Đây là Trang thông tin và hướng dẫn tự động về các Thủ tục hành chính thuộc thẩm quyền giải quyết của Công an xã An Viễn (Cư trú, Căn cước VNeID, Đăng ký xe, PCCC & CNCH, Trích lục hộ tịch, Tuyển quân & Tuyển sinh CAND).</p>
        <p>Anh/chị vui lòng chọn hoặc nhập nội dung cần hướng dẫn bên dưới.</p>
    </div>
    """, unsafe_allow_html=True)

# Khởi tạo biến prompt xử lý
prompt_to_process = None

# Danh sách nút gợi ý nhanh
st.markdown("**Gợi ý tra cứu thủ tục nhanh:**")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Đăng ký tạm trú VNeID"):
        prompt_to_process = "Thủ tục đăng ký tạm trú qua VNeID thực hiện như thế nào?"
    if st.button("Trích lục Hộ tịch DVC"):
        prompt_to_process = "Trình tự xin trích lục hộ tịch trên Cổng Dịch vụ công?"
with col2:
    if st.button("Đăng ký sang tên xe"):
        prompt_to_process = "Thủ tục sang tên xe máy và cấp lại biển số xe?"
    if st.button("Tuyển sinh CAND"):
        prompt_to_process = "Tiêu chuẩn và hồ sơ đăng ký tuyển sinh các trường Công an nhân dân?"
with col3:
    if st.button("An toàn PCCC nhà trọ"):
        prompt_to_process = "Hướng dẫn kiểm tra an toàn PCCC nhà trọ và số điện thoại báo cháy?"
    if st.button("SĐT Trực ban Công an xã"):
        prompt_to_process = "Số điện thoại trực ban Công an xã An Viễn?"

st.divider()

# Hiển thị Lịch sử Trò chuyện
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Nếu là câu trả lời của Trợ lý, cho phép Tải Phiếu Hướng Dẫn Hành Chính
        if message["role"] == "assistant":
            phieu_content = f"""CÔNG AN TỈNH ĐỒNG NAI             CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
CÔNG AN XÃ AN VIỄN                   Độc lập - Tự do - Hạnh phúc

PHIẾU HƯỚNG DẪN THỦ TỤC HÀNH CHÍNH
Ngày khởi tạo: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Địa điểm: Công an xã An Viễn, thành phố Đồng Nai
--------------------------------------------------------------------------------
{message['content']}
--------------------------------------------------------------------------------
Thông tin liên hệ hỗ trợ:
- Trực ban Công an xã An Viễn: 02513.538.187 (Trực 24/24)
- Số điện thoại khẩn cấp: 113 (An ninh trật tự), 114 (PCCC & CNCH)
"""
            st.download_button(
                "📥 In / Tải Phiếu Hướng Dẫn (.txt)",
                data=phieu_content,
                file_name=f"Phieu_Huong_Dan_Thu_Tuc_{idx}.txt",
                key=f"dl_{idx}"
            )

# Ô Nhập câu hỏi từ người dùng
user_input = st.chat_input("Nhập nội dung cần hỗ trợ hướng dẫn thủ tục...")
if user_input:
    prompt_to_process = user_input

# Xử lý khi có câu hỏi
if prompt_to_process:
    # 1. Thêm câu hỏi người dùng vào lịch sử và hiển thị
    st.session_state.messages.append({"role": "user", "content": prompt_to_process})
    with st.chat_message("user"):
        st.markdown(prompt_to_process)

    # 2. Xử lý phản hồi từ hệ thống RAG
    with st.chat_message("assistant"):
        with st.status("Đang tiếp nhận và kiểm tra hệ thống...", expanded=True) as status:
            st.write("Bước 1: Đang tiếp nhận và phân tích nội dung câu hỏi...")
            sub_queries = analyze_query(prompt_to_process)
            st.write(f"Đã phân tích thành {len(sub_queries)} nội dung cần tra cứu.")

            all_contexts = []
            any_need_web_search = False

            for sq in sub_queries:
                st.write(f"Bước 2: Đang đối chiếu Cơ sở dữ liệu nghiệp vụ và Danh bạ cán bộ phụ trách...")
                res = answer_query(sq)
                ctx = res["full_context"]
                
                st.write(f"Bước 3: Đánh giá độ phù hợp của văn bản pháp lý...")
                is_pass = check_context_relevance(sq, ctx)
                
                if is_pass and ctx:
                    st.write(f"Dữ liệu CSDL phù hợp.")
                    all_contexts.append(ctx)
                else:
                    st.write(f"Tra cứu thông tin mở trên Cổng Dịch vụ công Quốc gia.")
                    any_need_web_search = True
                    if ctx:
                        all_contexts.append(ctx)

            combined_context = "\n\n".join(all_contexts)

            if any_need_web_search:
                st.write("Bước 4: Tổng hợp quy định hướng dẫn bổ sung...")

            st.write("Bước 5: Đang soạn thảo văn bản trả lời chính thức...")
            llm_reply = get_llm_response(prompt_to_process, combined_context, need_web_search=any_need_web_search)
            
            status.update(label="Hoàn tất tra cứu", state="complete", expanded=False)

        st.markdown(llm_reply)
        
        # Tải Phiếu Hướng Dẫn Hành Chính
        phieu_content = f"""CÔNG AN TỈNH ĐỒNG NAI             CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
CÔNG AN XÃ AN VIỄN                   Độc lập - Tự do - Hạnh phúc

PHIẾU HƯỚNG DẪN THỦ TỤC HÀNH CHÍNH
Ngày khởi tạo: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Địa điểm: Công an xã An Viễn, thành phố Đồng Nai
--------------------------------------------------------------------------------
{llm_reply}
--------------------------------------------------------------------------------
Thông tin liên hệ hỗ trợ:
- Trực ban Công an xã An Viễn: 02513.538.187 (Trực 24/24)
- Số điện thoại khẩn cấp: 113 (An ninh trật tự), 114 (PCCC & CNCH)
"""
        st.download_button(
            "📥 In / Tải Phiếu Hướng Dẫn (.txt)",
            data=phieu_content,
            file_name=f"Phieu_Huong_Dan_Thu_Tuc_moi.txt",
            key="dl_new"
        )
        
        st.session_state.messages.append({"role": "assistant", "content": llm_reply})
