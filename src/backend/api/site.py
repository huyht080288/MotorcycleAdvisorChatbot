import json
import re
from collections import Counter

from fastapi import APIRouter

from backend.paths import DATAREF_DIR

router = APIRouter(prefix="/api", tags=["site"])

DATAREF_FILE = DATAREF_DIR / "minhlongmoto-com.json"

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
    {"name": "Dĩ An - Bình Dương", "address": "Số 27 Đường M, khu phố Nhị Đồng 2, Phường Dĩ An, TP HCM", "phone": "0967.674.456"},
    {"name": "Thuận An - Bình Dương", "address": "T1/60M, Khu Phố Bình Thuận 2, Phường Thuận Giao, TP HCM", "phone": "0975.156.879"},
    {"name": "Kha Vạn Cân - Thủ Đức", "address": "1260 Kha Vạn Cân, Phường Linh Xuân, TP HCM", "phone": "0918.868.357"},
    {"name": "QL1K - Thủ Đức", "address": "Số 6-8 Hoàng Cầm (Quốc Lộ 1K), P. Linh Xuân, TP HCM", "phone": "0898.888.618"},
    {"name": "Bình Thạnh", "address": "72-74 Đinh Bộ Lĩnh, Phường Bình Thạnh, TP HCM", "phone": "0898.888.816"},
    {"name": "Tân Bình", "address": "770 Trường Chinh, Phường Tân Sơn, TP HCM", "phone": "0967.841.939"},
    {"name": "Quận 12", "address": "117A Lê Văn Khương, Phường Tân Thới Hiệp, TP HCM", "phone": "0902.701.345"},
]

SERVICES = [
    {
        "id": "bao-duong",
        "icon": "🛠️",
        "title": "Tặng nhớt & bảo dưỡng",
        "description": "Ưu đãi bảo dưỡng lớn khi mua xe tại Minh Long Motor.",
        "question": "Cửa hàng có chương trình tặng nhớt và bảo dưỡng không?",
    },
    {
        "id": "bien-so",
        "icon": "🪪",
        "title": "Đăng ký biển số",
        "description": "Hỗ trợ thủ tục đăng ký biển số xe nhanh gọn.",
        "question": "Mua xe có hỗ trợ đăng ký biển số không?",
    },
    {
        "id": "van-chuyen",
        "icon": "🚚",
        "title": "Vận chuyển toàn quốc",
        "description": "Giao xe tận nơi trên toàn quốc.",
        "question": "Minh Long Motor có dịch vụ vận chuyển xe không?",
    },
    {
        "id": "tra-gop",
        "icon": "💳",
        "title": "Hỗ trợ trả góp",
        "description": "Thủ tục đơn giản, tư vấn phương án thanh toán phù hợp.",
        "question": "Mua xe trả góp cần những thủ tục gì?",
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

CARD_IMAGES = {
    "dat-bike-quantum-s2-gia-thanh-re-hieu-nang-vung-vang-285km-sac": "/assets/product-quantum-s2.jpg",
    "dat-bike-era-xe-ien-o-thi-200km-sac-cop-xe-50-lit": "https://minhlongmoto.com/wp-content/uploads/2022/02/dat-bike-era-1.jpg",
    "yamaha-neos-2026-ot-pha-3-mau-moi-gia-chi-36-9-trieu-ong": "https://minhlongmoto.com/wp-content/uploads/2022/02/yamaha-neos-2026.jpg",
    "vinfast-luot-he-phoi-phoi-giam-gia-xe-ien-16": "/assets/product-vinfast-km.jpg",
    "sieu-khuyen-mai-tvs-ntorq-125-giam-en-9-000-000-vnd": "/assets/product-tvs-ntorq.jpg",
    "gia-tvs-callisto-110-xe-tay-ga-thoi-trang-than-kim-loai": "https://minhlongmoto.com/wp-content/uploads/2023/11/tvs-callisto-110.jpg",
    "chao-he-rang-ro-cung-grande-song-xanh-luot-chat-cung-neos": "https://minhlongmoto.com/wp-content/uploads/2026/04/khuyen-mai-yamaha-grande.jpg",
    "mua-tpbw-125-rinh-qua-ang-cap-20-03-31-08-2026": "https://minhlongmoto.com/wp-content/uploads/2026/03/khuyen-mai-naga-150-2.jpg",
    "yamaha-grande-125-giam-trieu-khuyen-mai-so-luong-co-han": "https://minhlongmoto.com/wp-content/uploads/2025/12/khuyen-mai-grande-125.jpg",
    "uu-ai-9-9-trieu-cho-tvs-callisto-125": "https://minhlongmoto.com/wp-content/uploads/2024/06/uu-dai-3-trieu-cho-tvs-callisto-125.jpg",
    "giam-9-5-trieu-khi-mua-tvs-callisto-110": "https://minhlongmoto.com/wp-content/uploads/2024/06/giam-3-trieu-khi-mua-tvs-callisto-110.jpg",
    "hanh-trinh-tu-thien-2026-zontes-viet-nam-chia-se-yeu-thuong-ket-thuc-thanh-cong": "https://minhlongmoto.com/wp-content/uploads/2022/02/zontes-viet-nam-chia-se-yeu-thuong.jpg",
    "tvs-viet-nam-ong-hanh-cung-bike-week-viet-nam-2026": "https://minhlongmoto.com/wp-content/uploads/2026/03/tvs-viet-nam-tai-bike-week-2026.jpg",
    "zontes-368-703f-cung-bike-week-viet-nam-2026-cam-ranh-khanh-hoa": "https://minhlongmoto.com/wp-content/uploads/2026/03/zontes-tai-bike-week-2026-1.jpg",
    "xe-ga-nu-tvs-callisto-125-trinh-lang-gia-25-trieu-ong-nhap-khau": "https://minhlongmoto.com/wp-content/uploads/2023/11/tvs-callisto-125.jpg",
    "zontes-703t-ong-co-3-xi-lanh-he-lo-thong-tin-ra-mat-tai-viet-nam": "https://minhlongmoto.com/wp-content/uploads/2026/05/zontes-703t-5.jpg",
    "datbike-quantum-s1-xe-ien-hieu-nang-cao-100km-h": "https://minhlongmoto.com/wp-content/uploads/2025/10/datbike-quantum-s1.jpg",
    "giam-soc-xe-may-ien-honda-icon-e-chi-con-15-trieu-ong": "https://minhlongmoto.com/wp-content/uploads/2022/03/honda-icon-e-duoi-15-trieu.jpg",
    "vinfast-viper-2026-xe-ien-oi-pin-156-km-sac": "https://minhlongmoto.com/wp-content/uploads/2026/03/vinfast-viper.jpg",
    "vinfast-evo-ho-tro-oi-pin-tai-tram-165km-sac": "https://minhlongmoto.com/wp-content/uploads/2026/03/vinfast-evo.jpg",
    "honda-hooride-125-xe-ga-moi-ham-ho-nhu-adv-cong-nghe-nfc": "https://minhlongmoto.com/wp-content/uploads/2026/03/honda-hoodride-125-9.jpg",
    "nhan-coc-yamaha-r3-all-new-uu-ai-sap-san-en-34-trieu-chi-03-suat-duy-nhat": "https://minhlongmoto.com/wp-content/uploads/2026/06/uu-dai-yamaha-r3.jpg",
    "sym-naga-150-xe-tay-ga-moi-cho-thi-truong-viet-nam": "https://minhlongmoto.com/wp-content/uploads/2022/12/xe-tay-ga-sym-mmbcu.jpg",
    "xe-sym-attila-50-lua-chon-hoan-hao-cho-hoc-sinh-sinh-vien": "https://minhlongmoto.com/wp-content/uploads/2024/05/sym-attila-50cc.jpg",
    "sym-elegant-50-xe-so-50cc-binh-dan-cho-gia-inh": "https://minhlongmoto.com/wp-content/uploads/2024/04/sym-elegant-50-2.jpg",
    "sym-shark-50-xe-tay-ga-danh-cho-hoc-sinh-sinh-vien": "https://minhlongmoto.com/wp-content/uploads/2023/06/gia-sym-shark-50.jpg",
    "sym-priti-50cc-xe-tay-ga-hoc-uong-hoan-hao": "https://minhlongmoto.com/wp-content/uploads/2024/06/sym-priti-50-3.jpg",
    "xe-halim-cub-86-2026-xe-cub-50cc-sieu-tiet-kiem-nhien-lieu": "https://minhlongmoto.com/wp-content/uploads/2022/04/halim-cub-86-2.jpg",
}

CATEGORY_IMAGES = {
    "electric": "/assets/motorcycle-electric-category.webp",
    "petrol": "/assets/motorcycle-petrol-category.webp",
    "fifty_cc": "/assets/motorcycle-50cc-category.webp",
    "promo": "/assets/motorcycle-promotion-banner.webp",
    "service": "/assets/motorcycle-service-category.webp",
    "news": "/assets/motorcycle-news-category.webp",
    "price": "/assets/motorcycle-price-category.webp",
}

BRANDS = ["Honda", "Yamaha", "VinFast", "TVS", "SYM", "Zontes", "Suzuki", "Dat Bike", "GPX", "Halim"]


def _clean_title(question: str) -> str:
    for prefix in ("Thông tin về ", "Thông tin Giá ", "Thông tin "):
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


def _brand_for(text: str) -> str:
    normalized = text.lower().replace("datbike", "dat bike")
    for brand in BRANDS:
        if brand.lower() in normalized:
            return brand
    if "icon e" in normalized:
        return "Honda"
    return "Minh Long"


def _load_entries() -> list[dict]:
    if not DATAREF_FILE.exists():
        return []
    with DATAREF_FILE.open(encoding="utf-8") as f:
        data = json.load(f)
    return data.get("entries", [])


def _entry_card(entry: dict) -> dict:
    title = _clean_title(entry.get("question", ""))
    answer = entry.get("answer", "")
    entry_id = entry.get("id")
    category = _categorize(entry)
    return {
        "id": entry_id,
        "title": title,
        "summary": _clean_summary(answer),
        "price": _extract_price(answer) or _extract_price(title),
        "category": category,
        "brand": _brand_for(f"{title} {entry_id or ''}"),
        "image": CARD_IMAGES.get(entry_id),
        "badge": "Sale" if category == "promo" else ("Mới" if category in ("electric", "petrol") else ""),
        "source_url": entry.get("source_url", ""),
        "question": entry.get("question", title),
    }


def _unique_entries(entries: list[dict]) -> list[dict]:
    unique = []
    seen = set()
    for entry in entries:
        entry_id = entry.get("id") or ""
        source_url = entry.get("source_url") or entry_id
        if "-alt-" in entry_id or source_url in seen:
            continue
        seen.add(source_url)
        unique.append(entry)
    return unique


@router.get("/site-content")
def get_site_content() -> dict:
    entries = _load_entries()
    unique_entries = _unique_entries(entries)
    cards = [_entry_card(e) for e in unique_entries]

    by_id = {c["id"]: c for c in cards if c["id"]}
    featured = [by_id[fid] for fid in FEATURED_IDS if fid in by_id]

    if len(featured) < 4:
        priced = [c for c in cards if c.get("price") and c["category"] in ("electric", "petrol", "promo")]
        for card in priced:
            if card not in featured:
                featured.append(card)
            if len(featured) >= 6:
                break

    featured_ids = {c["id"] for c in featured}
    promos = [
        c for c in cards
        if c["category"] == "promo"
        and c["id"] != "khuyen-mai"
        and c["id"] not in featured_ids
        and c.get("image")
    ][:6]
    news = [
        c for c in cards
        if c["category"] == "news"
        and c["id"] not in featured_ids
        and c["id"] not in (
            "xin-chao",
            "cam-on",
            "tam-biet",
            "minh-long-motor-cua-hang-mua-xe-may-xe-ien-gia-tot",
        )
        and c["brand"] != "Minh Long"
    ][:6]
    collections = {
        category: [
            c for c in cards
            if c["category"] == category
            and c["id"] not in featured_ids
            and c.get("price")
            and c.get("image")
        ][:8]
        for category in ("electric", "petrol", "fifty_cc")
    }
    category_counts = Counter(c["category"] for c in cards)

    hero = {
        "title": "Mua xe máy, xe điện chính hãng giá tốt",
        "subtitle": "Đa dạng mẫu xe xăng, xe điện và xe 50cc. Hỗ trợ tư vấn, trả góp, biển số và giao xe tận nơi.",
        "highlights": [
            "Xe xăng & xe điện đa dạng",
            "Khuyến mãi cập nhật liên tục",
            "7 chi nhánh TP.HCM & Bình Dương",
        ],
    }

    categories = [
        {"id": "electric", "label": "Xe điện", "icon": "⚡", "image": CATEGORY_IMAGES["electric"], "target": "electric", "count": category_counts["electric"]},
        {"id": "petrol", "label": "Xe xăng", "icon": "🏍️", "image": CATEGORY_IMAGES["petrol"], "target": "petrol", "count": category_counts["petrol"]},
        {"id": "promo", "label": "Khuyến mãi", "icon": "🎁", "image": CATEGORY_IMAGES["promo"], "target": "promotions", "count": category_counts["promo"]},
        {"id": "price", "label": "Bảng giá", "icon": "💰", "image": CATEGORY_IMAGES["price"], "target": "featured", "count": category_counts["price"]},
        {"id": "fifty_cc", "label": "Xe 50cc", "icon": "🛵", "image": CATEGORY_IMAGES["fifty_cc"], "target": "fifty_cc", "count": category_counts["fifty_cc"]},
        {"id": "service", "label": "Dịch vụ", "icon": "🔧", "image": CATEGORY_IMAGES["service"], "target": "services", "count": category_counts["service"]},
    ]

    return {
        "store_name": "Minh Long Motor",
        "hotline": "0786.0000.36",
        "source": "https://minhlongmoto.com/",
        "hero": hero,
        "categories": categories,
        "featured": featured[:6],
        "promotions": promos,
        "collections": collections,
        "news": news,
        "brands": BRANDS,
        "services": SERVICES,
        "branches": BRANCHES,
        "quick_questions": QUICK_QUESTIONS,
        "entry_count": len(unique_entries),
        "raw_entry_count": len(entries),
    }
