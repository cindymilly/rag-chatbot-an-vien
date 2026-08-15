"""
embedder.py
-----------
Module quản lý Embedding Model cho hệ thống Hybrid Adaptive Correct RAG.
Mặc định dùng model tiếng Việt: bkai-foundation-models/vietnamese-bi-encoder
"""

import sys
from typing import List

_MODEL = None
_MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"

def get_model():
    """Lazy-load model, chỉ load 1 lần."""
    global _MODEL
    if _MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            print(f"[embedder] Đang khởi tạo model embedding: {_MODEL_NAME}...")
            _MODEL = SentenceTransformer(_MODEL_NAME)
            print("[embedder] Đã sẵn sàng model embedding.")
        except Exception as e:
            print(f"[embedder] Lỗi load model sentence_transformers: {e}")
            raise e
    return _MODEL

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Nhận vào list văn bản, trả về list vector embedding."""
    model = get_model()
    vectors = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True
    )
    return vectors.tolist()
