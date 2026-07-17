"""Scrape website URL and export DataRef JSON."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from tools.dataref_cleaner import clean_answer

SRC_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = SRC_DIR / "DataRef"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "entry"


def fetch_html(url: str, timeout: int = 15) -> str:
    headers = {"User-Agent": "motorcycle-advisor-chatbot/1.0"}
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.text


def extract_text(element) -> str:
    if element is None:
        return ""
    for tag in element.find_all(
        ["script", "style", "nav", "footer", "header", "aside", "form"]
    ):
        tag.decompose()
    for selector in (
        ".breadcrumb",
        ".breadcrumbs",
        ".rank-math-breadcrumb",
        ".comments-area",
        ".comment-list",
        ".sharedaddy",
        ".social-share",
        ".elementor-location-header",
        ".elementor-location-footer",
        "#comments",
    ):
        for node in element.select(selector):
            node.decompose()
    text = element.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text)


def collect_links(base_url: str, soup: BeautifulSoup, same_domain: str) -> list[str]:
    links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(base_url, anchor["href"])
        parsed = urlparse(href)
        if parsed.netloc != same_domain:
            continue
        if any(
            x in parsed.path
            for x in [
                "/tag/",
                "/author/",
                "/page/",
                "/comment-page-",
                "#",
                "javascript:",
            ]
        ):
            continue
        clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
        if clean not in links and clean != base_url.rstrip("/"):
            links.append(clean)
    return links


def page_to_entry(url: str, soup: BeautifulSoup) -> dict | None:
    title_tag = soup.find("h1") or soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""
    if not title:
        return None

    article = soup.find("article") or soup.find("main") or soup.body
    content = extract_text(article)
    if len(content) < 80:
        return None

    entry_id = slugify(title)[:80]
    answer = clean_answer(content, entry_id)[:1200]
    question = title if "?" in title else f"Thông tin về {title}"

    return {
        "id": entry_id,
        "question": question,
        "answer": answer,
        "tags": [w for w in re.findall(r"[A-Za-zÀ-ỹ0-9]{3,}", title)[:5]],
        "source_url": url,
    }


def scrape_site(start_url: str, max_pages: int = 20) -> dict:
    domain = urlparse(start_url).netloc
    visited: set[str] = set()
    queue = [start_url.rstrip("/")]
    entries: list[dict] = []
    seen_ids: set[str] = set()

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            html = fetch_html(url)
        except requests.RequestException:
            continue

        soup = BeautifulSoup(html, "lxml")
        entry = page_to_entry(url, soup)
        if entry and entry["id"] not in seen_ids:
            seen_ids.add(entry["id"])
            entries.append(entry)

        for link in collect_links(url, soup, domain):
            if link not in visited and link not in queue:
                queue.append(link)

    return {
        "source": start_url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Chuyển URL website thành file DataRef JSON")
    parser.add_argument("url", help="URL website nguồn, vd: https://minhlongmoto.com/")
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Đường dẫn file output (mặc định: DataRef/<domain>.json)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=20,
        help="Số trang tối đa crawl (mặc định: 20)",
    )
    args = parser.parse_args()

    domain = urlparse(args.url).netloc.replace(".", "-")
    output = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR / f"{domain}.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    print(f"Đang crawl: {args.url} (tối đa {args.max_pages} trang)...")
    data = scrape_site(args.url, max_pages=args.max_pages)

    with output.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Hoàn tất: {len(data['entries'])} entries → {output}")


if __name__ == "__main__":
    main()
