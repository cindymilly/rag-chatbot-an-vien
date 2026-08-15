"""
build_kb_collection.py
-----------------------
Build Vector Database (ChromaDB) từ tài liệu RAG-ready và các file processed Markdown.
Tạo 2 collections:
1. `kb_chunks`: Các chunk quy trình RAG chuẩn với KB_CHUNK_START/END
2. `source_chunks`: Các chunk tài liệu nguồn chi tiết (45 nguồn)
"""

import os
import re
import json
from pathlib import Path

import chromadb
from embedder import embed_texts

DATA_DIR = Path(__file__).parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
DB_DIR = Path(__file__).parent / "chroma_db"

def load_master_chunks():
    master_path = DATA_DIR / "Tai_lieu_RAG_ready_Chatbot_CA_An_Vien.md"
    if not master_path.exists():
        print(f"Lỗi: Không tìm thấy {master_path}")
        return []

    with open(master_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chunk_pattern = re.compile(r'<!-- KB_CHUNK_START (.*?) -->(.*?)<!-- KB_CHUNK_END -->', re.DOTALL)
    matches = chunk_pattern.findall(content)

    chunks = []
    for idx, (header_attr, chunk_body) in enumerate(matches):
        body_text = chunk_body.strip()
        if not body_text:
            continue
            
        attr_dict = {}
        for match in re.finditer(r'(\w+)="([^"]*)"', header_attr):
            attr_dict[match.group(1)] = match.group(2)
            
        chunk_id = attr_dict.get("id", f"CHUNK-{idx+1:04d}")
        topic = attr_dict.get("topic", "Nghiệp vụ Công an xã")
        
        chunks.append({
            "chunk_id": chunk_id,
            "topic": topic,
            "text": body_text
        })

    return chunks

def load_source_files():
    source_chunks = []
    if not PROCESSED_DIR.exists():
        return source_chunks

    for filename in sorted(os.listdir(PROCESSED_DIR)):
        if not filename.endswith('.md'):
            continue
        filepath = PROCESSED_DIR / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        # Split into sub-sections by ## or ###
        sections = re.split(r'\n(?=#{1,3}\s+)', text)
        for s_idx, sec in enumerate(sections):
            sec_clean = sec.strip()
            if len(sec_clean) < 30:
                continue
            lines = sec_clean.split('\n')
            title = lines[0].lstrip('#').strip()
            source_chunks.append({
                "source_id": filename.replace('.md', ''),
                "chunk_index": s_idx,
                "title": title,
                "text": sec_clean
            })

    return source_chunks

def main():
    print("=== BẮT ĐẦU NẠP DỮ LIỆU VÀO CHROMADB ===")
    
    # 1. Master KB Chunks
    kb_chunks = load_master_chunks()
    print(f"1. Đã tải {len(kb_chunks)} Master KB Chunks từ Tai_lieu_RAG_ready_Chatbot_CA_An_Vien.md.")

    # 2. Source Chunks
    src_chunks = load_source_files()
    print(f"2. Đã tải {len(src_chunks)} Source Chunks từ {len(os.listdir(PROCESSED_DIR))} file nguồn processed.")

    os.makedirs(DB_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=str(DB_DIR))

    # --- Build Collection 1: kb_chunks ---
    try:
        client.delete_collection("kb_chunks")
    except Exception:
        pass

    kb_coll = client.create_collection(
        name="kb_chunks",
        metadata={"hnsw:space": "cosine"}
    )

    kb_ids = [f"{c['chunk_id']}" for c in kb_chunks]
    kb_docs = [f"{c['topic']}\n\n{c['text']}" for c in kb_chunks]
    kb_metas = [{"chunk_id": c['chunk_id'], "topic": c['topic'], "text": c['text'][:1000]} for c in kb_chunks]

    print(f"Đang tính vector embedding cho {len(kb_docs)} Master KB Chunks...")
    kb_embeddings = embed_texts(kb_docs)

    BATCH = 200
    for i in range(0, len(kb_ids), BATCH):
        kb_coll.add(
            ids=kb_ids[i:i+BATCH],
            documents=kb_docs[i:i+BATCH],
            embeddings=kb_embeddings[i:i+BATCH],
            metadatas=kb_metas[i:i+BATCH]
        )
    print(f"✔ Đã nạp thành công {kb_coll.count()} vector vào collection 'kb_chunks'.")

    # --- Build Collection 2: source_chunks ---
    try:
        client.delete_collection("source_chunks")
    except Exception:
        pass

    src_coll = client.create_collection(
        name="source_chunks",
        metadata={"hnsw:space": "cosine"}
    )

    src_ids = [f"{c['source_id']}::chunk_{c['chunk_index']}" for c in src_chunks]
    src_docs = [f"{c['title']}\n\n{c['text']}" for c in src_chunks]
    src_metas = [{"source_id": c['source_id'], "title": c['title'], "text": c['text'][:1000]} for c in src_chunks]

    print(f"Đang tính vector embedding cho {len(src_docs)} Source Chunks...")
    src_embeddings = embed_texts(src_docs)

    for i in range(0, len(src_ids), BATCH):
        src_coll.add(
            ids=src_ids[i:i+BATCH],
            documents=src_docs[i:i+BATCH],
            embeddings=src_embeddings[i:i+BATCH],
            metadatas=src_metas[i:i+BATCH]
        )
    print(f"✔ Đã nạp thành công {src_coll.count()} vector vào collection 'source_chunks'.")
    print("=== HOÀN TẤT XÂY DỰNG CHROMADB ===")

if __name__ == "__main__":
    main()
