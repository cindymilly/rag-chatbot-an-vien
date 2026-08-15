"""
streamlit_app.py
----------------
Ứng dụng Web Streamlit cho Cổng Thông Tin Hướng Dẫn Thủ Tục Hành Chính - Công An Xã An Viễn.
Triển khai miễn phí 24/7 trên Streamlit Community Cloud.
"""

import os
import sys
import time
import streamlit as st

# Thiết lập API Key từ Streamlit Secrets hoặc Môi trường
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

from chatbot import analyze_query, check_context_relevance, get_llm_response
from query import answer_query

# Cấu hình Trang Streamlit
st.set_page_config(
    page_title="Cổng Thông Tin Hướng Dẫn Thủ Tục Hành Chính - Công An Xã An Viễn",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS giao diện Xanh Navy Công an Nhân dân (Không emoji/AI)
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
        font-size: 1.3rem;
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
    .stButton>button {
        background-color: #f1f5f9;
        color: #0b5394;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 500;
        padding: 6px 14px;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #0b5394;
        color: #ffffff;
        border-color: #0b5394;
    }
    .status-box {
        background-color: #f8fafc;
        border: 1px stroke #e2e8f0;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Header
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
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
        st.session_state.messages.append({"role": "assistant", "content": llm_reply})
