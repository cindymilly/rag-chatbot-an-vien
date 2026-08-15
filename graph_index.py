"""
graph_index.py
--------------
Module Graph Generator & Entity Context (Context 2 trong kiến trúc Hybrid Adaptive Correct RAG).
Xây dựng chỉ mục thực thể và mối quan hệ giữa các cán bộ, quy trình thủ tục, số điện thoại, điều luật PCCC/Cư trú/GPLX.
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

class EntityGraphIndex:
    def __init__(self):
        self.contacts = [
            {"name": "Trần Thị Minh Huệ", "title": "Thượng tá - Trưởng Công an xã", "phone": "0908.304.266", "role": "Phụ trách chung"},
            {"name": "Nguyễn Viết Cường", "title": "Trung tá - Phó Trưởng CA xã", "phone": "0915.559.645", "role": "Phụ trách Tổ Tổng hợp"},
            {"name": "Hoàng Chiến Thắng", "title": "Trung tá - Phó Trưởng CA xã", "phone": "0909.542.599", "role": "Phụ trách Tổ Trật tự"},
            {"name": "Nguyễn Văn Viên", "title": "Trung tá - Phó Trưởng CA xã", "phone": "0989.325.325", "role": "Phụ trách Tổ Phòng chống tội phạm"},
            {"name": "Phạm Tiến Dũng", "title": "Trung tá - Phó Trưởng CA xã", "phone": "0914.728.779", "role": "Phụ trách Tổ An ninh"},
            {"name": "Nguyễn Thế Lam", "title": "Thiếu tá - Phó Trưởng CA xã", "phone": "0983.137.968", "role": "Phụ trách Tổ Khu vực"},
            {"name": "Nguyễn Văn Định", "title": "Đại úy - CSKV", "phone": "0903.060.308", "role": "Ấp An Phú"},
            {"name": "Hà Văn Bằng", "title": "Thượng úy - CSKV", "phone": "0372.170.117", "role": "Ấp An Phú"},
            {"name": "Phạm Lê Minh", "title": "Đại úy - CSKV", "phone": "0973.520.521", "role": "Ấp Phát Đạt"},
            {"name": "Vũ Văn Mong", "title": "Thiếu tá - CSKV", "phone": "0937.813.979", "role": "Ấp Hưng Thịnh"},
            {"name": "Bùi Thị Thương", "title": "Đại úy", "phone": "0988.544.757", "role": "Cư trú & Dữ liệu dân cư"},
            {"name": "Lê Đình Quý", "title": "Đại úy", "phone": "0783.279.168", "role": "Cư trú & Dữ liệu dân cư"},
            {"name": "Trần Hữu Trang", "title": "Đại úy", "phone": "0908.066.600", "role": "Đăng ký xe"},
            {"name": "Lê Văn Phong", "title": "Trung tá", "phone": "0918.550.798", "role": "Phòng cháy chữa cháy (PCCC)"},
            {"name": "Bùi Phương Định", "title": "Trung tá", "phone": "0913.399.988", "role": "Tạm trú người nước ngoài"},
            {"name": "Phạm Xuân Sang", "title": "Thượng úy", "phone": "0989.327.407", "role": "Tuyển sinh & Nghĩa vụ CAND"},
            # TTPVHCC Hộ tịch & DVC
            {"name": "Lưu Thị Bích Huyền", "title": "Chuyên viên TTPVHCC", "phone": "0933.736.133", "role": "Hộ tịch, trích lục hộ tịch"},
            {"name": "Hoàng Thị Giang", "title": "Chuyên viên VPHĐND_UBND", "phone": "0913.224.009", "role": "Lĩnh vực Hộ tịch"},
            {"name": "Bùi Xuân Kiên", "title": "Chuyên viên VPHĐND_UBND", "phone": "0916.213.611", "role": "Chứng thực, Hộ tịch"},
            {"name": "Nguyễn Thanh Liêm", "title": "Chuyên viên TTPVHCC", "phone": "0979.724.427", "role": "Hỗ trợ kết quả TTHC, thu phí/lệ phí"}
        ]
        
        self.hotlines = {
            "trực ban công an xã": "02513.538.187",
            "công an xã an viễn": "02513.538.187",
            "an ninh trật tự": "113 (Khẩn cấp) hoặc 02513.538.187",
            "pccc": "114 (Báo cháy toàn quốc) hoặc 0918.550.798 (Trung tá Lê Văn Phong)",
            "cháy nổ": "114 (Báo cháy toàn quốc)",
            "cấp cứu": "115"
        }

    def search_graph_context(self, query: str) -> str:
        """Truy vấn các thực thể liên quan từ Graph DB / Structured Index."""
        q_lower = query.lower()
        matched_info = []

        # Matched Hotlines
        for key, val in self.hotlines.items():
            if key in q_lower:
                matched_info.append(f"- SĐT Khẩn cấp / Trực ban ({key.upper()}): {val}")

        # Matched Officers
        for c in self.contacts:
            if c["name"].lower() in q_lower or c["role"].lower() in q_lower or any(word in q_lower for word in c["role"].lower().split()):
                matched_info.append(f"- Cán bộ phụ trách: {c['title']} - {c['name']} (SĐT: {c['phone']}) - Lĩnh vực: {c['role']}")

        if matched_info:
            return "\n".join(matched_info[:5])
        return ""

_graph_instance = None
def get_graph_index():
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = EntityGraphIndex()
    return _graph_instance
