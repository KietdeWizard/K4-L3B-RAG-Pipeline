"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path
from urllib.request import Request, urlopen


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

LEGAL_SOURCES = {
    "luat-du-lich-2017.pdf": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2017/07/09.signed.pdf",
    "nghi-dinh-168-2017-nd-cp.pdf": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2017/01/168.signed.pdf",
    "thong-tu-06-2017-tt-bvhttdl.pdf": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2017/07/06.signed.pdf",
}


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai."""
    for filename, url in LEGAL_SOURCES.items():
        destination = DATA_DIR / filename
        request = Request(url, headers={"User-Agent": "K4-L3B-RAG-Pipeline/1.0"})
        with urlopen(request, timeout=60) as response:
            content = response.read()
        if len(content) <= 1024:
            raise ValueError(f"Downloaded file is too small: {url}")
        destination.write_bytes(content)
        print(f"Saved: {destination} ({len(content)} bytes)")


if __name__ == "__main__":
    setup_directory()
    download_documents()
