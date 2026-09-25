"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng MarkItDown để convert PDF/DOCX.
    2. Đọc JSON và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.

Cài đặt:
    Dependency MarkItDown đã được khai báo trong pyproject.toml.
    
-> Hoặc dùng công cụ nào bạn quen khác Markitdown
"""

from pathlib import Path
import json


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    from pypdf import PdfReader

    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(legal_dir.iterdir()):
        if path.suffix.lower() != ".pdf":
            continue
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        content = "\n\n".join(pages).strip()
        if len(content) < 200:
            content = (
                "This PDF has no usable text layer in the current environment. "
                "Keep the original PDF as the authoritative source and run OCR "
                "before indexing this document."
            )
        output = output_dir / f"{path.stem}.md"
        output.write_text(
            f"# {path.stem.replace('-', ' ').title()}\n\n"
            f"**Source:** {path.name}\n\n---\n\n{content}\n",
            encoding="utf-8",
        )


def convert_news_articles() -> None:
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(news_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        required = {"url", "title", "date_crawled", "content_markdown"}
        if not required <= data.keys() or len(data["content_markdown"].strip()) < 200:
            raise ValueError(f"Invalid article JSON: {path}")
        header = (
            f"# {data['title']}\n\n"
            f"**Source:** {data['url']}\n\n"
            f"**Crawled:** {data['date_crawled']}\n\n---\n\n"
        )
        (output_dir / f"{path.stem}.md").write_text(
            header + data["content_markdown"].strip() + "\n", encoding="utf-8"
        )


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
