"""
query.py
--------
Truy vấn dữ liệu từ Vector DB (Context 1) và Graph DB / Entity Index (Context 2).
"""

import sys
from pathlib import Path
import chromadb

from embedder import embed_texts
from graph_index import get_graph_index

DB_DIR = Path(__file__).parent / "chroma_db"

def search_vector_db(query: str, top_k: int = 4):
    """Tìm kiếm trong Vector DB (ChromaDB)"""
    if not DB_DIR.exists():
        return []

    client = chromadb.PersistentClient(path=str(DB_DIR))
    q_emb = embed_texts([query])[0]

    results = []
    
    # 1. Search kb_chunks
    try:
        kb_coll = client.get_collection("kb_chunks")
        res_kb = kb_coll.query(query_embeddings=[q_emb], n_results=top_k)
        for doc, meta, dist in zip(res_kb["documents"][0], res_kb["metadatas"][0], res_kb["distances"][0]):
            sim = 1 - dist
            results.append({
                "source": "Master KB",
                "sim": sim,
                "title": meta.get("topic", "Nghiệp vụ"),
                "text": meta.get("text", doc)
            })
    except Exception:
        pass

    # 2. Search source_chunks
    try:
        src_coll = client.get_collection("source_chunks")
        res_src = src_coll.query(query_embeddings=[q_emb], n_results=top_k)
        for doc, meta, dist in zip(res_src["documents"][0], res_src["metadatas"][0], res_src["distances"][0]):
            sim = 1 - dist
            results.append({
                "source": meta.get("source_id", "Source Doc"),
                "sim": sim,
                "title": meta.get("title", "Tài liệu nguồn"),
                "text": meta.get("text", doc)
            })
    except Exception:
        pass

    # Sort by similarity descending
    results.sort(key=lambda x: x["sim"], reverse=True)
    return results[:top_k]

def answer_query(query: str) -> dict:
    """
    Trả về bộ Context kép:
    - Context 1: Vector DB Context
    - Context 2: Graph DB / Entity Context
    - Similarity Score cao nhất
    """
    # 1. Context 2: Graph / Entity DB
    graph_idx = get_graph_index()
    graph_context = graph_idx.search_graph_context(query)

    # 2. Context 1: Vector DB
    vector_matches = search_vector_db(query, top_k=4)

    vector_texts = []
    max_sim = 0.0
    for m in vector_matches:
        if m["sim"] > max_sim:
            max_sim = m["sim"]
        vector_texts.append(f"--- [Nguồn: {m['source']} | Topic: {m['title']} | Độ khớp: {m['sim']:.2f}] ---\n{m['text']}")

    vector_context = "\n\n".join(vector_texts)

    combined_context_parts = []
    if graph_context:
        combined_context_parts.append(f"=== THÔNG TIN THỰC THỂ & DANH BẠ (GRAPH CONTEXT) ===\n{graph_context}")
    if vector_context:
        combined_context_parts.append(f"=== TRÍ THỨC TRIỂN KHẢI TỪ CSDL (VECTOR DB CONTEXT) ===\n{vector_context}")

    full_context = "\n\n".join(combined_context_parts)

    return {
        "full_context": full_context,
        "max_similarity": max_sim,
        "has_graph_match": bool(graph_context),
        "has_vector_match": bool(vector_context)
    }
