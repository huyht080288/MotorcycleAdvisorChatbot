"""Bổ sung biến thể câu hỏi ngắn cho file DataRef JSON."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

PREFIX = "Thông tin về "
BRANDS = (
    "Honda",
    "Yamaha",
    "VinFast",
    "Dat Bike",
    "TVS",
    "Suzuki",
    "GPX",
    "Zontes",
    "SYM",
    "Kawasaki",
    "BMW",
    "Halim",
)


def normalize_key(text: str) -> str:
    text = unicodedata.normalize("NFC", text.strip().lower())
    text = re.sub(r"\s+", " ", text)
    return text


def is_garbage_question(text: str) -> bool:
    if not text or len(text) < 4:
        return True
    if "JFIF" in text or "\x00" in text:
        return True
    letters = sum(1 for c in text if c.isalpha() or c in "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ")
    if letters < len(text) * 0.35:
        return True
    return False


def head_topic(core: str) -> str:
    head = core.split(" – ", 1)[0].strip()
    if ": " in head:
        head = head.split(": ", 1)[0].strip()
    return head


def generate_variants(entry: dict) -> list[dict]:
    q = entry["question"].strip()
    answer = entry["answer"]
    tags = entry.get("tags") or []
    entry_id = entry["id"]
    source_url = entry.get("source_url", "")
    out: list[dict] = []
    seen: set[str] = {normalize_key(q)}
    counter = 0

    def add(question: str) -> None:
        nonlocal counter
        question = re.sub(r"\s+", " ", question.strip())
        if len(question) < 4:
            return
        key = normalize_key(question)
        if key in seen:
            return
        seen.add(key)
        counter += 1
        out.append(
            {
                "id": f"{entry_id}-alt-{counter}",
                "question": question,
                "answer": answer,
                "tags": tags,
                "source_url": source_url,
            }
        )

    if q.startswith(PREFIX):
        core = q[len(PREFIX) :].strip()
        topic = head_topic(core)

        add(topic)

        if " – " in core:
            tail = core.split(" – ", 1)[1].strip().rstrip("?")
            if 4 < len(tail) <= 55:
                add(tail)

        if ": " in core:
            brand, rest = core.split(": ", 1)
            add(brand.strip())
            if " – " in rest:
                add(rest.split(" – ", 1)[0].strip())

        topic_lower = topic.lower()

        if "minh long motor" in topic_lower:
            add("Thông tin về Minh Long Motor")
            add("Minh Long Motor là gì?")
            add("Giới thiệu Minh Long Motor")
            add("Cửa hàng xe máy Minh Long Motor")
            add("Mua xe máy xe điện ở đâu?")

        if "bảng giá" in topic_lower:
            add("Bảng giá xe máy")
            add("Giá xe máy 2026")
            add("Xem bảng giá xe")

        if topic_lower == "khuyến mãi":
            add("Có khuyến mãi gì không?")
            add("Ưu đãi hiện tại")
            add("Chương trình khuyến mãi xe máy")

        if topic_lower == "xe xăng":
            add("Review xe xăng")
            add("Tin tức xe xăng")

        if topic_lower == "xe điện":
            add("Có những mẫu xe điện nào?")
            add("Giá xe điện")

        if topic_lower == "faq":
            add("Câu hỏi thường gặp")
            add("Minh Long Motor là gì?")

        if topic_lower == "dịch vụ":
            add("Dịch vụ cửa hàng")
            add("Bảo dưỡng xe máy")

        if any(b.lower() in topic.lower() for b in BRANDS) and len(topic) <= 55:
            for brand in BRANDS:
                if brand.lower() in topic.lower():
                    add(f"Giá {topic}")
                    add(f"Thông tin {topic}")
                    break
    else:
        if len(q) > 45 and "?" in q:
            add(q.split("?", 1)[0].strip() + "?")
        if "winner r" in q.lower():
            add("Giá Honda Winner R 2026")
            add("Honda Winner R 2026")

    return out


def manual_short_entries() -> list[dict]:
    base_url = "https://minhlongmoto.com"
    return [
        {
            "id": "small-talk-xin-chao-khong-dau",
            "question": "xin chao",
            "answer": "Em chào anh/chị ạ! Anh/chị cần tư vấn giá xe, mẫu xe, khuyến mãi hay địa chỉ cửa hàng ạ?",
            "tags": ["chào hỏi"],
            "source_url": base_url,
        },
        {
            "id": "small-talk-hello",
            "question": "hello",
            "answer": "Hello anh/chị! Em có thể tư vấn giá xe, mẫu xe và khuyến mãi tại Minh Long Motor ạ.",
            "tags": ["chào hỏi"],
            "source_url": base_url,
        },
        {
            "id": "small-talk-chao-shop",
            "question": "chào shop",
            "answer": "Dạ em chào anh/chị! Em có thể hỗ trợ tư vấn xe máy, xe điện và dịch vụ của Minh Long Motor ạ.",
            "tags": ["chào hỏi"],
            "source_url": base_url,
        },
        {
            "id": "small-talk-cam-on",
            "question": "cảm ơn",
            "answer": "Dạ không có chi ạ! Nếu cần thêm thông tin về giá xe hoặc khuyến mãi, anh/chị cứ hỏi em nhé.",
            "tags": ["chào hỏi"],
            "source_url": base_url,
        },
        {
            "id": "faq-minh-long-la-gi",
            "question": "Minh Long Motor là gì?",
            "answer": "Minh Long Motor là cửa hàng, siêu thị xe máy chuyên kinh doanh xe số, tay ga, côn tay, xe điện và dịch vụ bảo dưỡng tại Bình Dương.",
            "tags": ["Minh Long Motor", "FAQ"],
            "source_url": f"{base_url}/faq",
        },
        {
            "id": "faq-dia-chi-minh-long",
            "question": "Địa chỉ Minh Long Motor",
            "answer": "Minh Long Motor có chi nhánh tại Bình Dương (ví dụ Dĩ An). Anh/chị có thể hỏi em chi nhánh gần nhất hoặc xem trang Liên hệ trên website.",
            "tags": ["địa chỉ", "Minh Long Motor"],
            "source_url": f"{base_url}/faq",
        },
        {
            "id": "faq-dang-ky-bien-so",
            "question": "Minh Long Motor có hỗ trợ ra biển số không?",
            "answer": "Có ạ. Minh Long Motor hỗ trợ dịch vụ đăng ký biển số xe khi khách mua xe tại cửa hàng.",
            "tags": ["biển số", "dịch vụ"],
            "source_url": f"{base_url}/faq",
        },
    ]


def enrich_file(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    original_entries = data.get("entries", [])

    cleaned = [e for e in original_entries if not is_garbage_question(e.get("question", ""))]
    removed = len(original_entries) - len(cleaned)

    enriched: list[dict] = []
    seen_questions: set[str] = set()

    def append_unique(entry: dict) -> None:
        key = normalize_key(entry["question"])
        if key in seen_questions:
            return
        seen_questions.add(key)
        enriched.append(entry)

    for entry in manual_short_entries():
        append_unique(entry)

    for entry in cleaned:
        append_unique(entry)
        for variant in generate_variants(entry):
            append_unique(variant)

    data["entries"] = enriched
    data["enriched_at"] = data.get("scraped_at")
    return {
        "data": data,
        "original_count": len(original_entries),
        "cleaned_count": len(cleaned),
        "removed_garbage": removed,
        "final_count": len(enriched),
        "added_variants": len(enriched) - len(cleaned) - len(manual_short_entries()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich DataRef JSON with short question variants")
    parser.add_argument("file", type=Path, help="Path to DataRef JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Print stats only")
    args = parser.parse_args()

    result = enrich_file(args.file)
    print(
        f"original={result['original_count']} "
        f"removed_garbage={result['removed_garbage']} "
        f"final={result['final_count']} "
        f"added_variants={result['added_variants']}"
    )

    if not args.dry_run:
        args.file.write_text(
            json.dumps(result["data"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Saved: {args.file}")


if __name__ == "__main__":
    main()
