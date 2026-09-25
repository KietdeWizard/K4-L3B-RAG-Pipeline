# Individual contribution report

## Thông tin

- Họ và tên: Nguyen Minh Kiet
- Mã học viên: 2A202602373
- Nhóm: Lab 08 — Vietnam Tourism RAG Pipeline
- Repository/branch: `K4-L3B-RAG-Pipeline` / `main`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Data collection and provenance | Collected three official legal PDFs and five Vietnam Travel pages; retained landing files and documented every source. | `data/landing/`, `docs/CORPUS_SOURCES.md`, commit `64808b7` | Done |
| Data standardization and indexing | Implemented conversion to Markdown, stable chunk IDs, local 1024-dimensional embeddings, and idempotent Chroma upsert. | `src/task1_collect_legal_docs.py`–`src/task5_semantic_search.py`, `data/standardized/`, commit `64808b7` | Done |
| Hybrid retrieval and fallback | Implemented BM25, RRF, dense-score thresholding, and failure-safe PageIndex integration; corrected lexical fallback behavior. | `src/task6_lexical_search.py`–`src/task9_retrieval_pipeline.py`, commits `64808b7`, `47ab1d5` | Done |
| Citation-aware generation and UI | Implemented provider dispatch, local grounded generation, source-preserving citations, safe refusal, and Streamlit source expanders. | `src/task10_generation.py`, `app.py`, commits `64808b7`, `47ab1d5` | Done |
| Evaluation and submission | Created the 15-case golden dataset, A/B report, teammate record, corpus documentation, and ran repository checks. | `group_project/evaluation/`, `TEAMMATES.md`, commit `64808b7` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng `HashingVectorizer` 1024 chiều cho embedding mặc định.  
   **Lý do/evidence:** Index và query dùng chung `embed_texts()`, chạy lại ổn định và không cần API key trả phí; contract tests kiểm tra việc dùng chung hàm embedding.  
   **Trade-off:** Chất lượng ngữ nghĩa thấp hơn embedding model chuyên dụng, nên BM25 và RRF cần hỗ trợ các truy vấn có tên riêng/mã văn bản.

2. **Quyết định:** Chỉ so sánh fallback threshold với cosine score gốc của dense retrieval; khi evidence yếu và không có fallback thì trả về rỗng để generation từ chối an toàn.  
   **Lý do/evidence:** `src/task9_retrieval_pipeline.py` tuân thủ module contract; `tests/test_contracts.py` bao phủ quyết định theo dense score, provider error, và fallback không khả dụng.  
   **Trade-off:** Có thể từ chối một số câu hỏi đúng chủ đề nếu threshold 0.30 chưa được hiệu chỉnh với nhiều query hơn.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest tests/test_contracts.py -q`, `pytest tests/test_acceptance.py -q`, và các query demo về Hoi An, Phu Quoc, mã văn bản pháp lý, cùng query ngoài domain.
- Kết quả trước/sau nếu có: hybrid + RRF đạt trung bình 0.84 so với 0.75 của dense-only trong bảng đánh giá 15 câu; context recall tăng nhiều nhất, từ 0.71 lên 0.84.
- Lỗi đã phát hiện và cách xử lý: BM25 trên corpus nhỏ có thể có IDF không dương; đã bổ sung điểm lexical-overlap ổn định. Local answerer từng chọn navigation text; đã lọc menu/link nhiễu và xếp hạng sentence theo query-term overlap.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: ba PDF pháp lý không có text layer dùng được, nên hiện chỉ truy vấn được metadata/ghi chú nguồn chứ không truy vấn chi tiết điều khoản.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: OCR ba PDF, loại bỏ navigation không liên quan khỏi news Markdown, sau đó chạy lại cùng golden dataset để hiệu chỉnh threshold và đo A/B.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-25
- Tên thành viên: Nguyen Minh Kiet
