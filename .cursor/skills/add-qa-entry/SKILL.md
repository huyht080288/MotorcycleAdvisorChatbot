---
name: add-qa-entry
description: Thêm hoặc sửa cặp question-answer trong file DataRef JSON. Dùng khi bổ sung kiến thức thủ công, sửa câu trả lời sai, hoặc mở rộng knowledge base.
---

# Thêm / sửa Q&A trong DataRef

## Thêm entry mới

Mở file `src/DataRef/<file>.json`, thêm vào mảng `entries`:

```json
{
  "id": "honda-wave-alpha-gia",
  "question": "Giá Honda Wave Alpha bao nhiêu?",
  "answer": "Honda Wave Alpha có giá từ 18.500.000 đồng tùy phiên bản.",
  "tags": ["Honda", "Wave Alpha", "giá"],
  "source_url": ""
}
```

## Quy tắc `id`

- Unique trong file
- Slug: chữ thường, dấu gạch ngang, không dấu tiếng Việt

## Sau khi sửa

1. Lưu file JSON
2. Admin → chọn file (và các file liên quan) → **Train** lại
3. Test chat với câu hỏi mới

## Gợi ý viết `question`

Viết 1–2 cách hỏi tự nhiên mà khách thường dùng; TF-IDF khớp theo từ khóa nên đặt tên xe, giá, dịch vụ trong câu hỏi.
