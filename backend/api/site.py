import json
import re
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["site"])

ROOT = Path(__file__).resolve().parents[2]
DATAREF_FILE = ROOT / "DataRef" / "minhlongmoto-com.json"

CATEGORY_RULES = [
    ("electric", ["xe-dien", "dat-bike", "vinfast", "honda-icon", "yamaha-neos", "quantum"]),
    ("promo", ["khuyen-mai"]),
    ("petrol", ["review-xe", "xe-xang", "yamaha", "honda-hoo", "mx-king", "lc135", "kawasaki", "sym-naga"]),
    ("fifty_cc", ["xe-50cc", "-50", "halim-cub"]),
    ("service", ["dich-vu", "tang-nhot", "dang-ky-bien", "van-chuyen", "phu-tung"]),
    ("contact", ["lien-he", "gioi-thieu"]),
    ("price", ["bang-gia"]),
]

BRANCHES = [
    {"name": "Dĩ An - Bình Dương", "address": "Số 27 Đường M, khu phố Nhị Đồng 2, Phường Dĩ An"},
    {"name": "Thuận An - Bình Dương", "address": "T1/60M, Khu Phố Bình Thuận 2, Phường Thuận Giao"},
    {"name": "Kha Vạn Cân - Thủ Đức", "address": "1260 Kha Vạn Cân, Phường Linh Xuân"},
    {"name": "QL1K - Thủ Đức", "address": "Số 6-8 Hoàng Cầm (Quốc Lộ 1K), P. Linh Xuân"},
    {"name": "Bình Thạnh", "address": "72-74 Đinh Bộ Lĩnh, Phường Bình Thạnh"},
    {"name": "Tân Bình", "address": "770 Trường Chinh, Phường Tân Sơn"},
    {"name": "Quận 12", "address": "117A Lê Văn Khương, Phường Tân Thới Hiệp"},
]

SERVICES = [
    {
        "id": "bao-duong",
        "title": "Tặng nhớt & bảo dưỡng",
        "description": "Ưu đãi bảo dưỡng lớn khi mua xe tại Minh Long Motor.",
        "question": "Cửa hàng có chương trình tặng nhớt và bảo dưỡng không?",
    },
    {
        "id": "bien-so",
        "title": "Đăng ký biển số",
        "description": "Hỗ trợ thủ tục đăng ký biển số xe nhanh gọn.",
        "question": "Mua xe có hỗ trợ đăng ký biển số không?",
    },
    {
        "id": "van-chuyen",
        "title": "Vận chuyển toàn quốc",
        "description": "Giao xe tận nơi trên toàn quốc.",
        "question": "Minh Long Motor có dịch vụ vận chuyển xe không?",
    },
]

QUICK_QUESTIONS = [
    "Bảng giá xe máy 2026",
    "Khuyến mãi hiện tại có gì?",
    "Giá Dat Bike Quantum S2 bao nhiêu?",
    "Có xe điện VinFast không?",
    "Địa chỉ cửa hàng ở Dĩ An?",
    "TVS Callisto 125 giá bao nhiêu?",
]

FEATURED_IDS = [
    "dat-bike-quantum-s2-gia-thanh-re-hieu-nang-vung-vang-285km-sac",
    "dat-bike-era-xe-ien-o-thi-200km-sac-cop-xe-50-lit",
    "yamaha-neos-2026-ot-pha-3-mau-moi-gia-chi-36-9-trieu-ong",
    "vinfast-luot-he-phoi-phoi-giam-gia-xe-ien-16",
    "sieu-khuyen-mai-tvs-ntorq-125-giam-en-9-000-000-vnd",
    "gia-tvs-callisto-110-xe-tay-ga-thoi-trang-than-kim-loai",
]


def _clean_title(question: str) -> str:
    for prefix in ("Thông tin về ", "Thông tin "):
        if question.startswith(prefix):
            return question[len(prefix) :].strip()
    return question.strip()


def _clean_summary(answer: str, max_len: int = 140) -> str:
    text = answer
    for junk in (
        "Trang Chủ",
        "Theo dõi Minhlongmoto.com trên",
        "Các ý chính trong bài viết",
        "Minh Long Motor",
    ):
        text = text.replace(junk, " ")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "..."


def _extract_price(text: str) -> str | None:
    patterns = [
        r"(\d{1,3}(?:[.,]\d{3})+(?:\s*VNĐ|\s*đồng))",
        r"(\d{1,2}[.,]\d+\s*triệu\s*đồng)",
        r"giá\s*(\d{1,2}[.,]\d+\s*triệu)",
        r"(\d{2}[.,]\d{3}[.,]\d{3})\s*đồng",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _categorize(entry: dict) -> str:
    url = (entry.get("source_url") or "").lower()
    entry_id = (entry.get("id") or "").lower()
    haystack = f"{url} {entry_id}"
    for category, keywords in CATEGORY_RULES:
        if any(k in haystack for k in keywords):
            return category
    return "news"


def _load_entries() -> list[dict]:
    if not DATAREF_FILE.exists():
        return []
    with DATAREF_FILE.open(encoding="utf-8") as f:
        data = json.load(f)
    return data.get("entries", [])


def _entry_card(entry: dict) -> dict:
    title = _clean_title(entry.get("question", ""))
    answer = entry.get("answer", "")
    return {
        "id": entry.get("id"),
        "title": title,
        "summary": _clean_summary(answer),
        "price": _extract_price(answer) or _extract_price(title),
        "category": _categorize(entry),
        "source_url": entry.get("source_url", ""),
        "question": entry.get("question", title),
    }


@router.get("/site-content")
def get_site_content() -> dict:
    entries = _load_entries()
    cards = [_entry_card(e) for e in entries]

    by_id = {c["id"]: c for c in cards if c["id"]}
    featured = [by_id[fid] for fid in FEATURED_IDS if fid in by_id]

    if len(featured) < 4:
        priced = [c for c in cards if c.get("price") and c["category"] in ("electric", "petrol", "promo")]
        for card in priced:
            if card not in featured:
                featured.append(card)
            if len(featured) >= 6:
                break

    promos = [c for c in cards if c["category"] == "promo"][:4]
    news = [c for c in cards if c["category"] in ("petrol", "electric", "news")][:6]

    hero_entry = by_id.get("minh-long-motor-cua-hang-mua-xe-may-xe-ien-gia-tot")
    hero = {
        "title": "Minh Long Motor",
        "subtitle": "Cửa hàng xe máy & xe điện chính hãng — giá tốt, tư vấn tận tâm",
        "highlights": [
            "Xe xăng & xe điện đa dạng",
            "Khuyến mãi cập nhật liên tục",
            "7 chi nhánh TP.HCM & Bình Dương",
        ],
    }
    if hero_entry:
        hero["subtitle"] = hero_entry.get("summary") or hero["subtitle"]

    categories = [
        {"id": "electric", "label": "Xe điện", "icon": "⚡", "question": "Có những mẫu xe điện nào?"},
        {"id": "petrol", "label": "Xe xăng", "icon": "🏍️", "question": "Minh Long có những dòng xe xăng nào?"},
        {"id": "promo", "label": "Khuyến mãi", "icon": "🎁", "question": "Khuyến mãi hiện tại có gì?"},
        {"id": "price", "label": "Bảng giá", "icon": "💰", "question": "Bảng giá xe máy 2026"},
        {"id": "fifty_cc", "label": "Xe 50cc", "icon": "🛵", "question": "Có xe 50cc không cần bằng lái không?"},
        {"id": "service", "label": "Dịch vụ", "icon": "🔧", "question": "Cửa hàng có những dịch vụ gì?"},
    ]

    return {
        "store_name": "Minh Long Motor",
        "hotline": "0786.0000.36",
        "source": "https://minhlongmoto.com/",
        "hero": hero,
        "categories": categories,
        "featured": featured[:6],
        "promotions": promos,
        "news": news,
        "services": SERVICES,
        "branches": BRANCHES,
        "quick_questions": QUICK_QUESTIONS,
        "entry_count": len(entries),
    }
