# Individual contribution report

## Thông tin

- Họ và tên: Đào Minh Hiếu
- Mã học viên: 2A202602561
- Nhóm: Lab 08 — Vietnam Tourism RAG Pipeline
- Repository/branch: `K4-L3B-RAG-Pipeline` / `main`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Retrieval pipeline | Hỗ trợ kiểm tra luồng dense search và BM25, kết quả RRF, điều kiện chuyển sang PageIndex fallback và giới hạn `top_k`; đối chiếu đầu ra với contract chung của `SearchResult`. | `src/task5_semantic_search.py`–`src/task9_retrieval_pipeline.py`, `tests/test_contracts.py`; phiên bản nhóm tại commit `abb6aa3` | Done |
| Citation flow | Kiểm tra việc giữ lại metadata nguồn khi sắp xếp context, định dạng nhãn `Document`, và trả về đầy đủ `answer`, `sources`, `retrieval_source` để câu trả lời có thể truy vết về tài liệu. | `src/task10_generation.py`, `src/contracts.py`, `tests/test_contracts.py`; phiên bản nhóm tại commit `abb6aa3` | Done |
| Chatbot verification | Hỗ trợ kiểm chứng chatbot với câu hỏi trong miền du lịch, trường hợp evidence yếu/ngoài miền và nhánh không có API key; xác nhận giao diện hiển thị câu trả lời cùng danh sách nguồn đã dùng. | `app.py`, `src/task10_generation.py`, `tests/test_acceptance.py`; phiên bản nhóm tại commit `abb6aa3` | Done |
| Evaluation support | Đối chiếu hành vi retrieval/generation với kết quả A/B của nhóm, đặc biệt cải thiện của hybrid + RRF và cơ chế từ chối an toàn khi không đủ bằng chứng. | `group_project/evaluation/RESULT.md`, `group_project/evaluation/golden_dataset.json` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng hybrid retrieval (dense + BM25) và RRF làm luồng mặc định; chỉ kích hoạt fallback dựa trên cosine score gốc của dense retrieval.
   **Lý do/evidence:** Dense search hỗ trợ truy vấn ngữ nghĩa, còn BM25 tìm tốt tên địa danh, mã văn bản và tên nguồn chính xác. Kết quả đánh giá của nhóm cho thấy hybrid + RRF đạt trung bình 0.84, cao hơn 0.75 của dense-only; context recall tăng từ 0.71 lên 0.84.
   **Trade-off:** Phải chạy hai phương pháp tìm kiếm trước khi hợp nhất nên độ trễ cao hơn dense-only; threshold 0.30 vẫn cần được hiệu chỉnh trên nhiều truy vấn hơn.

2. **Quyết định:** Luôn bảo toàn metadata và danh sách nguồn qua bước generation; khi không có evidence phù hợp thì trả về safe refusal thay vì tạo câu trả lời không được kiểm chứng.
   **Lý do/evidence:** `format_context()` gắn title, source, retrieval method và score vào từng context; `generate_with_citation()` trả lại cả `sources` và `retrieval_source`. Contract tests cũng kiểm tra nguồn trong context, nhánh fallback và trường hợp không có evidence.
   **Trade-off:** Chatbot có thể từ chối một số câu hỏi liên quan nhưng có điểm retrieval thấp; đổi lại câu trả lời an toàn hơn và người dùng có thể kiểm tra nguồn.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest tests/test_contracts.py -q`, `pytest tests/test_acceptance.py -q`; các query kiểm tra về Hội An, Phú Quốc, tên/mã văn bản pháp lý và câu hỏi ngoài phạm vi corpus.
- Kết quả trước/sau nếu có: cấu hình hybrid + RRF cải thiện cả bốn chỉ số so với dense-only; điểm trung bình tăng từ 0.75 lên 0.84, trong đó context recall tăng mạnh nhất (+0.13).
- Lỗi đã phát hiện và cách xử lý: evidence yếu có thể bị dùng để trả lời nếu fallback không tìm thấy kết quả; luồng retrieval hiện trả danh sách rỗng trong trường hợp này để generation kích hoạt safe refusal. Citation được giữ qua metadata và hiển thị cùng câu trả lời để có thể truy vết.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: việc kiểm chứng hiện dựa trên corpus nhỏ và ba PDF pháp lý chưa có text layer dùng được, nên chưa đánh giá đầy đủ câu hỏi chi tiết theo điều khoản pháp luật.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: bổ sung bộ query gắn nhãn gồm cả in-domain và out-of-domain, đo precision/recall của safe refusal, sau đó hiệu chỉnh threshold 0.30 và kiểm tra lại citation sau khi OCR các PDF.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-26
- Tên thành viên: Đào Minh Hiếu
