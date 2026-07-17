"""Làm sạch boilerplate website khỏi câu trả lời DataRef."""

from __future__ import annotations

import re

ARTICLE_HEADER_RE = re.compile(
    r"^Trang Chủ\s+.+?\s+"
    r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\s+"
    r"Theo dõi\s+Minhlongmoto\.com\s+trên\s+",
    re.IGNORECASE,
)
ALT_SUFFIX_RE = re.compile(r"-alt-\d+$")
TOC_MARKER = "Các ý chính trong bài viết"
REGISTRATION_SELECTOR_RE = re.compile(
    r"Chọn nơi làm biển số\s+Nơi ra biển số\s+"
    r"TP\.HCM, Hà Nội\s+Thành phố \(trừ TP\.HCM, Hà Nội\)\s+Thị xã\s+Huyện\s*",
    re.IGNORECASE,
)

CATEGORY_BREADCRUMBS = sorted(
    (
        "Trang Chủ Xe xăng Xe 50cc",
        "Trang Chủ Xe xăng Kawasaki",
        "Trang Chủ Xe xăng Yamaha",
        "Trang Chủ Xe xăng Zontes",
        "Trang Chủ Xe xăng Honda",
        "Trang Chủ Xe xăng GPX",
        "Trang Chủ Xe xăng SYM",
        "Trang Chủ Xe xăng TVS",
        "Trang Chủ Hỗ trợ cộng đồng",
        "Trang Chủ GIAO THÔNG",
        "Trang Chủ Khuyến mãi",
        "Trang Chủ Tuyển dụng",
        "Trang Chủ Về chúng tôi",
        "Trang Chủ Dịch vụ",
        "Trang Chủ Xe điện",
        "Trang Chủ Xe xăng",
    ),
    key=len,
    reverse=True,
)

MANUAL_ANSWERS = {
    "minh-long-motor-cua-hang-mua-xe-may-xe-ien-gia-tot": (
        "Minh Long Motor là hệ thống kinh doanh xe máy và xe điện chính hãng, "
        "cung cấp nhiều dòng xe xăng, xe điện, xe 50cc cùng dịch vụ trả góp, "
        "đăng ký biển số, bảo dưỡng và vận chuyển xe."
    ),
    "van-chuyen": (
        "Minh Long Motor hỗ trợ vận chuyển xe tận nơi. Phạm vi giao xe, chi phí "
        "và thời gian nhận xe phụ thuộc địa chỉ của khách hàng; vui lòng liên hệ "
        "cửa hàng để được báo phương án cụ thể."
    ),
    "tvs-norton-atlas-gt-mau-mo-to-ia-hinh-600cc-lo-hinh-anh-au-tien": (
        "TVS Norton Atlas GT là mẫu mô tô địa hình dung tích khoảng 600cc được "
        "hé lộ với thiết kế thiên về touring và adventure. Thông tin giá bán và "
        "thời điểm phân phối tại Việt Nam chưa được xác nhận."
    ),
    "tvs-apache-rtx-300-mau-adventure-thong-minh-nhat-2026": (
        "TVS Apache RTX 300 là mẫu xe adventure 300cc hướng đến khả năng đi phố "
        "và đường dài, nổi bật với thiết kế đa dụng và các trang bị hỗ trợ người "
        "lái. Giá bán thực tế tùy thời điểm phân phối."
    ),
    "chao-he-rang-ro-cung-grande-song-xanh-luot-chat-cung-neos": (
        "Chương trình “Chào hè rạng rỡ cùng Grande – Sống xanh, lướt chất cùng "
        "Neo’s” áp dụng cho các mẫu Yamaha Grande và Neo’s trong thời gian ưu "
        "đãi. Khách hàng nên liên hệ cửa hàng để kiểm tra quà tặng và phiên bản "
        "còn áp dụng."
    ),
    "yamaha-lc135-ra-mat-4-mau-moi-gia-chi-47-trieu-ong": (
        "Yamaha LC135 được giới thiệu với bốn màu mới, thiết kế xe số thể thao "
        "và mức giá tham khảo khoảng 47 triệu đồng. Giá tại cửa hàng có thể thay "
        "đổi theo phiên bản, màu xe và thời điểm."
    ),
    "chinh-hang-yzf-r3-2026-all-new-khoi-au-hanh-trinh-moi": (
        "Yamaha YZF-R3 2026 All New là mẫu sportbike chính hãng dành cho người "
        "mới làm quen phân khối lớn, có thiết kế thể thao và tư thế lái cân bằng. "
        "Vui lòng liên hệ cửa hàng để kiểm tra giá và lịch nhận xe."
    ),
    "gia-tvs-callisto-110-xe-tay-ga-thoi-trang-than-kim-loai": (
        "TVS Callisto 110 là mẫu xe tay ga nhập khẩu có thiết kế thời trang, thân "
        "xe kim loại chắc chắn và hướng đến nhu cầu di chuyển hằng ngày. Giá bán "
        "tùy phiên bản và chương trình ưu đãi tại thời điểm mua."
    ),
}


def base_entry_id(entry_id: str) -> str:
    return ALT_SUFFIX_RE.sub("", entry_id)


def _strip_toc(text: str) -> str:
    marker_index = text.find(TOC_MARKER)
    if marker_index < 0:
        return text

    before = text[:marker_index].strip()
    remainder = text[marker_index + len(TOC_MARKER) :].strip()
    without_first_number = re.sub(r"^1(?:\.\d+)*\s+", "", remainder)
    words = without_first_number.split()

    for token_count in range(min(14, len(words)), 3, -1):
        phrase = " ".join(words[:token_count])
        repeated_at = without_first_number.find(phrase, len(phrase))
        if repeated_at >= 0:
            content = without_first_number[repeated_at:].strip()
            return f"{before} {content}".strip() if before else content

    return text


def _strip_category_breadcrumb(text: str) -> str:
    for breadcrumb in CATEGORY_BREADCRUMBS:
        if text.startswith(breadcrumb):
            return text[len(breadcrumb) :].strip()
    return text


def clean_answer(answer: str, entry_id: str = "") -> str:
    """Trả về answer đã bỏ metadata giao diện nhưng giữ nội dung chính."""
    manual = MANUAL_ANSWERS.get(base_entry_id(entry_id))
    if manual:
        return manual

    original = re.sub(r"\s+", " ", (answer or "")).strip()
    if not original:
        return original

    cleaned = ARTICLE_HEADER_RE.sub("", original, count=1).strip()
    cleaned = _strip_category_breadcrumb(cleaned)
    cleaned = _strip_toc(cleaned)
    cleaned = REGISTRATION_SELECTOR_RE.sub("", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned or original
