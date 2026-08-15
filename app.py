"""
app.py
------
Flask Web Server phục vụ giao diện RAG Chatbot Công an xã An Viễn.
Sử dụng Server-Sent Events (SSE) để stream trực quan từng bước của luồng "Hybrid Adaptive Correct RAG":
User Query -> Query Analyzer -> Multi-Step Reasoning -> Vector DB (Context 1) + Graph DB (Context 2) -> Grader (PASS/FAIL) -> [Web Search Fallback] -> LLM Output
"""

import json
import time
import os
from flask import Flask, render_template, request, Response

from chatbot import analyze_query, check_context_relevance, get_llm_response
from query import answer_query

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_input = data.get("message", "").strip()

    if not user_input:
        return Response("data: {\"status\": \"error\", \"message\": \"Câu hỏi trống\"}\n\n", mimetype="text/event-stream")

    def generate():
        def send_event(status, message, details=None, is_final=False):
            payload = {
                "status": status,
                "message": message,
                "details": details or "",
                "is_final": is_final
            }
            return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        # Step 1: Query Analyzer
        yield send_event("analyzing", "Bước 1: Đang tiếp nhận và phân tích nội dung câu hỏi...")
        sub_queries = analyze_query(user_input)
        time.sleep(0.2)

        yield send_event("analyzed", f"Đã phân tích thành {len(sub_queries)} nội dung cần tra cứu.", details=sub_queries)

        all_contexts = []
        any_need_web_search = False

        # Step 2 & 3: Retrieval & Grader for each sub-query
        for sq in sub_queries:
            yield send_event("retrieving", f"Bước 2: Đang đối chiếu Cơ sở dữ liệu nghiệp vụ và Danh bạ cán bộ phụ trách...")
            res = answer_query(sq)
            ctx = res["full_context"]
            max_sim = res["max_similarity"]
            time.sleep(0.2)

            yield send_event("grading", f"Bước 3: Đánh giá độ phù hợp của văn bản pháp lý...")
            is_pass = check_context_relevance(sq, ctx)
            time.sleep(0.2)

            if is_pass and ctx:
                yield send_event("pass", f"Dữ liệu CSDL phù hợp.")
                all_contexts.append(ctx)
            else:
                yield send_event("fail", f"Tra cứu thông tin mở trên Cổng Dịch vụ công Quốc gia.")
                any_need_web_search = True
                if ctx:
                    all_contexts.append(ctx)

        combined_context = "\n\n".join(all_contexts)

        # Step 4: Web Search Fallback if needed
        if any_need_web_search:
            yield send_event("web_search", "Bước 4: Tổng hợp quy định hướng dẫn bổ sung...")
            time.sleep(0.3)

        # Step 5: LLM Synthesis Generation
        yield send_event("generating", "Bước 5: Đang soạn thảo văn bản trả lời chính thức...")
        llm_reply = get_llm_response(user_input, combined_context, need_web_search=any_need_web_search)

        yield send_event("done", llm_reply, is_final=True)

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\nKhởi chạy Server Web RAG Chatbot Công an xã An Viễn trên port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
