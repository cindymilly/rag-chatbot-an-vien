"""
streamlit_app.py
----------------
Cổng Thông Tin Hướng Dẫn Thủ Tục Hành Chính - Công An Xã An Viễn
Tích hợp các tính năng nâng cao:
1. Bộ lọc tra cứu Cán bộ Công an phụ trách theo từng Ấp
2. Thanh bên Tải Mẫu đơn Hành chính Công dạng Microsoft Word (.docx) chuẩn Nghị định 30/2020/NĐ-CP
3. Tải / In Phiếu Hướng dẫn Thủ tục Hành chính chuẩn Microsoft Word (.docx) Times New Roman 13pt
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
from docx_generator import create_legal_docx

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
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-left: 4px solid #0b5394 !important;
        padding: 12px 14px;
        border-radius: 4px;
        margin-bottom: 8px;
        color: #0f172a !important;
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
# THANH BÊN (SIDEBAR) - KHÔNG EMOJI
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### CÔNG AN XÃ AN VIỄN")
    st.markdown("**Trực ban 24/24:** `02513.538.187`")
    st.divider()

    # 1. BỘ LỌC TRA CỨU CÁN BỘ PHỤ TRÁCH THEO ĐỊA BÀN
    st.markdown("### Cán Bộ Phụ Trách Theo Địa Bàn")
    selected_ap = st.selectbox(
        "Chọn đơn vị / địa bàn tra cứu:",
        [
            "Tất cả cán bộ & Ban chỉ chỉ huy",
            "Ban Chỉ huy Công an xã",
            "Ấp An Phú",
            "Ấp Phát Đạt",
            "Ấp Hưng Thịnh",
            "Cán bộ Chuyên môn & Hộ tịch"
        ]
    )

    graph = get_graph_index()
    all_contacts = graph.contacts

    filtered_contacts = all_contacts
    if selected_ap == "Ban Chỉ huy Công an xã":
        filtered_contacts = [c for c in all_contacts if "Trưởng" in c.get("title", "") or "Chỉ huy" in c.get("role", "")]
    elif selected_ap == "Ấp An Phú":
        filtered_contacts = [c for c in all_contacts if "An Phú" in c.get("role", "") or "An Phú" in c.get("title", "")]
    elif selected_ap == "Ấp Phát Đạt":
        filtered_contacts = [c for c in all_contacts if "Phát Đạt" in c.get("role", "") or "Phát Đạt" in c.get("title", "")]
    elif selected_ap == "Ấp Hưng Thịnh":
        filtered_contacts = [c for c in all_contacts if "Hưng Thịnh" in c.get("role", "") or "Hưng Thịnh" in c.get("title", "")]
    elif selected_ap == "Cán bộ Chuyên môn & Hộ tịch":
        filtered_contacts = [c for c in all_contacts if "Trưởng" not in c.get("title", "") and "Ấp" not in c.get("role", "")]

    with st.container(height=320):
        for c in filtered_contacts:
            st.markdown(f"""
            <div class="officer-card">
                <strong style="color: #0b5394 !important; font-weight: bold; font-size: 0.9rem;">{c['title']} - {c['name']}</strong><br/>
                <span style="color: #1e293b !important; font-size: 0.85rem;">SĐT: <strong style="color: #0f172a !important;">{c['phone']}</strong></span><br/>
                <span style="color: #475569 !important; font-size: 0.8rem;">Phụ trách: {c['role']}</span>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # 2. DANH SÁCH MẪU ĐƠN HÀNH CHÍNH (FILE WORD .DOCX)
    st.markdown("### Tải Mẫu Đơn Hành Chính (File Word)")
    
    st.markdown("**Mẫu CT01 - Tờ khai Cư trú**")
    st.caption("Tờ khai thay đổi thông tin cư trú chuẩn Word (.docx)")
    ct01_md = """### TỜ KHAI THAY ĐỔI THÔNG TIN CƯ TRÚ (Mẫu CT01)
Kính gửi: Công an xã An Viễn, thành phố Đồng Nai

1. Họ và tên: ........................................................
2. Ngày, tháng, năm sinh: ....../....../............ Giới tính: ..........
3. Số định danh cá nhân/CCCD: .......................................
4. Số điện thoại liên hệ: .............................................
5. Nơi thường trú hiện tại: ...........................................
6. Nơi tạm trú/Nơi ở hiện tại: ........................................
7. Nội dung đề nghị: .................................................
(Ví dụ: Đăng ký thường trú / Đăng ký tạm trú / Khai báo tạm vắng)
"""
    ct01_docx = create_legal_docx("Mẫu CT01 Tờ khai cư trú", ct01_md, "Mau_CT01")
    st.download_button("Tải Mẫu CT01 (.docx)", data=ct01_docx, file_name="Mau_CT01_To_Khai_Cu_Tru.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    st.markdown("**Mẫu CT07 - Giấy Xác Nhận Cư Trú**")
    st.caption("Đơn xin cấp xác nhận thông tin cư trú chuẩn Word (.docx)")
    ct07_md = """### ĐƠN XIN CẤP GIẤY XÁC NHẬN THÔNG TIN VỀ CƯ TRÚ (Mẫu CT07)
Kính gửi: Công an xã An Viễn, thành phố Đồng Nai

Tôi tên là: ...........................................................
Số CCCD: .......................... Ngày cấp: .......... Nơi cấp: .......
Địa chỉ thường trú: ....................................................
Yêu cầu cấp Giấy xác nhận thông tin về cư trú để làm thủ tục: .........
"""
    ct07_docx = create_legal_docx("Mẫu CT07 Xác nhận cư trú", ct07_md, "Mau_CT07")
    st.download_button("Tải Mẫu CT07 (.docx)", data=ct07_docx, file_name="Mau_CT07_Xac_Nhan_Cu_Tru.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    st.markdown("**Mẫu MĐ01 - Khai Đăng Ký Xe**")
    st.caption("Giấy khai đăng ký xe máy, ô tô chuẩn Word (.docx)")
    md01_md = """### GIẤY KHAI ĐĂNG KÝ XE (Mẫu MĐ01)
Kính gửi: Công an xã An Viễn, thành phố Đồng Nai

Tên chủ xe: ...........................................................
Địa chỉ: ..............................................................
Số CCCD: .............................................................
Nhãn hiệu xe: ................ Loại xe: .......... Màu sơn: ...........
Số khung: .............................................................
Số máy: ...............................................................
Lý do đề nghị: (Đăng ký mới / Sang tên / Cấp lại biển số xe)
"""
    md01_docx = create_legal_docx("Mẫu MĐ01 Khai đăng ký xe", md01_md, "Mau_MD01")
    st.download_button("Tải Mẫu MĐ01 (.docx)", data=md01_docx, file_name="Mau_MD01_Dang_Ky_Xe.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

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
        # Nếu là câu trả lời của Trợ lý, cho phép Tải Phiếu Hướng Dẫn Hành Chính (.docx)
        if message["role"] == "assistant":
            docx_data = create_legal_docx("Phiếu Hướng Dẫn Thủ Tục", message['content'], f"Phieu_{idx}")
            st.download_button(
                "In / Tải Phiếu Hướng Dẫn (.docx)",
                data=docx_data,
                file_name=f"Phieu_Huong_Dan_Thu_Tuc_{idx}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
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
        
        # Tải Phiếu Hướng Dẫn Hành Chính chuẩn Word (.docx)
        docx_data = create_legal_docx("Phiếu Hướng Dẫn Thủ Tục", llm_reply, "Phieu_Moi")
        st.download_button(
            "In / Tải Phiếu Hướng Dẫn (.docx)",
            data=docx_data,
            file_name=f"Phieu_Huong_Dan_Thu_Tuc_Moi.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="dl_new"
        )
        
        st.session_state.messages.append({"role": "assistant", "content": llm_reply})
