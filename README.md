# CỔNG THÔNG TIN TRI THỨC VÀ HƯỚNG DẪN THỦ TỤC HÀNH CHÍNH - CÔNG AN XÃ AN VIỄN

## 1. Giới thiệu Tổng quan
Hệ thống Cổng thông tin tri thức và hỗ trợ giải đáp thủ tục hành chính công trực tuyến thuộc quản lý chuyên môn của **Công an xã An Viễn, thành phố Đồng Nai**.

Hệ thống được xây dựng nhằm mục đích nâng cao hiệu quả công tác tiếp công dân, hướng dẫn công khai, minh bạch các trình tự, thủ tục hành chính thuộc thẩm quyền giải quyết của lực lượng Công an cấp xã, hỗ trợ người dân thực hiện các thủ tục trên môi trường điện tử (Cổng Dịch vụ công Bộ Công an, Cổng Dịch vụ công Quốc gia, Ứng dụng VNeID).

---

## 2. Kiến trúc Hệ thống Xử lý Dữ liệu

```text
[Yêu cầu từ Công dân]
         │
         ▼
[Bộ Phân Tách Nội Dung & Phân Loại Ý Định]
         │
         ├────────────────────────────────────────┐
         ▼                                        ▼
[Cơ Sở Dữ Liệu Vector ChromaDB]          [Chỉ Mục Thực Thể & Danh Bạ Nghiệp Vụ]
(1.827 Khối Tri Thức Quy Chuẩn)          (15 Cán Bộ, Hotlines & Đơn Vị Tiếp Nhận)
         │                                        │
         └───────────────────┬────────────────────┘
                             │
                             ▼
              [Bộ Đánh Giá Độ Hợp Quy Pháp Lý]
                             │
                             ▼
            [Tổng Hợp Văn Bản Trả Lời Chính Thức]
                             │
                             ▼
                   [Kết Quả Hướng Dẫn]
```

- **Mô hình nhúng văn bản (Embedding Model)**: Sử dụng mô hình xử lý ngôn ngữ tiếng Việt chuyên dụng `bkai-foundation-models/vietnamese-bi-encoder`.
- **Cơ sở dữ liệu Vector (Vector Database)**: Lưu trữ và tìm kiếm theo thuật toán k-NN trên bộ dữ liệu 1.827 khối tri thức nghiệp vụ đã được chuẩn hóa.
- **Chỉ mục Thực thể & Danh bạ (Entity Graph Index)**: Lưu trữ cấu trúc tổ chức, phân công địa bàn của 15 cán bộ, chiến sĩ Công an xã An Viễn và số điện thoại tiếp nhận phản ánh an ninh trật tự, PCCC.
- **Giao diện Web & Truyền dữ liệu**: Khởi chạy trên nền tảng Flask Server với cơ chế truyền dữ liệu thời gian thực Server-Sent Events (SSE).

---

## 3. Phạm vi Bộ Tri thức Nghiệp vụ

Bộ dữ liệu tri thức tích hợp trong hệ thống bao gồm đầy đủ các văn bản quy phạm pháp luật và hướng dẫn nghiệp vụ hiện hành:

1. **Thủ tục Cư trú & Định danh điện tử**:
   - Luật Cư trú số 68/2020/QH14, Nghị định 154/2024/NĐ-CP, Thông tư 66/2023/TT-BCA.
   - Hướng dẫn Đăng ký thường trú, Đăng ký tạm trú, Gia hạn tạm trú, Xóa đăng ký thường trú/tạm trú, Khai báo tạm vắng, Thông báo lưu trú.
   - Hướng dẫn sử dụng Tài khoản định danh điện tử VNeID Mức 1, Mức 2 và khôi phục mật khẩu.

2. **Thủ tục Đăng ký Xe & Giấy phép lái xe**:
   - Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15, Thông tư 79/2024/TT-BCA, Thông tư 51/2025/TT-BCA.
   - Trình tự Đăng ký xe mới trực tuyến toàn trình, Sang tên đổi chủ xe, Cấp đổi/Cấp lại chứng nhận đăng ký xe và biển số định danh.
   - Quy định Cấp đổi, Cấp lại Giấy phép lái xe theo Thông tư 108/2026/TT-BCA.

3. **Công tác Phòng cháy chữa cháy và Cứu nạn cứu hộ (PCCC & CNCH)**:
   - Luật PCCC & CNCH số 55/2024/QH15, Nghị định 105/2025/NĐ-CP, Nghị định 106/2025/NĐ-CP, Thông tư 36/2025/TT-BCA.
   - 40 Bộ tài liệu Hướng dẫn, Quy chuẩn QCVN (QCVN 06:2022/BXD, QCVN 10:2025/BCA) và Tiêu chuẩn TCVN (TCVN 3890:2023, TCVN 7435-1:2004, TCVN 7568:2025).
   - Kỹ năng thoát nạn, an toàn PCCC nhà trọ, chung cư mini, cơ sở kinh doanh, mô hình Tổ liên gia an toàn PCCC.

4. **Ngành nghề kinh doanh có điều kiện về ANTT**:
   - Nghị định 96/2016/NĐ-CP, Nghị định 56/2023/NĐ-CP, Nghị định 58/2026/NĐ-CP.
   - Trách nhiệm của chủ cơ sở lưu trú, nhà trọ, dịch vụ cầm đồ, karaoke, massage.

5. **Tuyển chọn nghĩa vụ CAND & Tuyển sinh các trường CAND**:
   - Tiêu chuẩn, hồ sơ tuyển chọn công dân thực hiện nghĩa vụ CAND theo Nghị định 184/2025/NĐ-CP.
   - Quy định tuyển sinh Đại học chính quy, Văn bằng 2 và Trung cấp CAND (Đổi mới hình thức thi trên máy tính từ năm 2026-2028).

6. **Trích lục Hộ tịch & Thông tin liên hệ Công an xã An Viễn**:
   - Danh bạ hotline hỗ trợ Cổng Dịch vụ công tại Trung tâm Phục vụ Hành chính công xã An Viễn.
   - Số điện thoại Trực ban Công an xã An Viễn: **02513.538.187** (Trực 24/24).
   - Danh bạ 15 cán bộ phụ trách các khu vực Ấp An Phú, Ấp Phát Đạt, Ấp Hưng Thịnh.

---

## 4. Cấu trúc Thư mục Nguồn (Repository Structure)

```text
rag_pipeline/
├── README.md                   # Tài liệu hướng dẫn hệ thống
├── Procfile                    # Cấu hình khởi chạy trên môi trường Production
├── render.yaml                 # Cấu hình triển khai tự động trên Cloud (Render)
├── requirements.txt            # Danh mục các thư viện phụ thuộc Python
├── app.py                      # Server Flask phục vụ xử lý và kết nối giao diện
├── chatbot.py                  # Lõi xử lý phân tích và tổng hợp văn bản trả lời
├── query.py                    # Động cơ truy vấn dữ liệu Vector và Thực thể
├── graph_index.py              # Chỉ mục danh bạ cán bộ và tổ chức nghiệp vụ
├── embedder.py                 # Mô hình tính toán vector embedding tiếng Việt
├── build_kb_collection.py      # Script khởi tạo CSDL ChromaDB từ kho tri thức
├── templates/
│   └── index.html              # Giao diện Cổng thông tin (Chuẩn văn bản hành chính)
└── chroma_db/                  # Cơ sở dữ liệu Vector DB đã hoàn hoãn nạp 1.827 vectors
```

---

## 5. Hướng dẫn Cài đặt và Khởi chạy

### 5.1 Cài đặt môi trường địa phương
```bash
# 1. Truy cập thư mục dự án
cd rag_pipeline

# 2. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 3. Khởi tạo Cơ sở dữ liệu Vector (chạy 1 lần ban đầu hoặc khi cập nhật dữ liệu)
python build_kb_collection.py

# 4. Khởi chạy Server
python app.py
```
Mở trình duyệt web và truy cập địa chỉ: `http://127.0.0.1:5000`

### 5.2 Triển khai trên môi trường Cloud (Production)
Dự án đã được tích hợp sẵn các file cấu hình tiêu chuẩn (`Procfile`, `render.yaml`):
- **Web Server**: Chạy qua WSGI Gunicorn Server (`gunicorn app:app`).
- **Biến môi trường**: Cấu hình `GEMINI_API_KEY` trong phần Environment Variables của dịch vụ Cloud.

---

## 6. Đơn vị Quản lý & Trực ban
- **Đơn vị áp dụng**: Công an xã An Viễn, thành phố Đồng Nai.
- **Địa chỉ trụ sở**: Ấp Phát Đạt, xã An Viễn, thành phố Đồng Nai.
- **Số điện thoại Trực ban 24/24**: 02513.538.187.
