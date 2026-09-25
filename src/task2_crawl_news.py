"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://vietnam.travel/things-to-do/10-must-try-hanoi-dishes",
    "https://vietnam.travel/things-to-do/10-delicious-vietnamese-rolls",
    "https://vietnam.travel/places-to-go/central-vietnam/hoi-an",
    "https://vietnam.travel/plan-your-trip/itineraries",
    "https://vietnam.travel/places-to-go/southern-vietnam/phu-quoc",
]


async def crawl_article(url: str) -> dict:
    try:
        from crawl4ai import AsyncWebCrawler

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            markdown = result.markdown
            title = result.metadata.get("title", "")
    except ImportError:
        request = Request(url, headers={"User-Agent": "K4-L3B-RAG-Pipeline/1.0"})
        with urlopen(request, timeout=60) as response:
            html = response.read().decode("utf-8", errors="replace")
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else url
        body = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", html, flags=re.I | re.S)
        body = re.sub(r"<[^>]+>", " ", body)
        body = re.sub(r"\s+", " ", body).strip()
        markdown = f"# {title}\n\n{body}"

    if len(markdown.strip()) < 200:
        raise ValueError(f"Crawled content is too short: {url}")
    return {
        "url": url,
        "title": title or "Vietnam Travel article",
        "date_crawled": datetime.now(timezone.utc).isoformat(),
        "content_markdown": markdown,
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
