---
name: train-from-dataref
description: Train AI từ nhiều file DataRef JSON qua admin UI hoặc API. Dùng khi admin chọn file JSON, rebuild TF-IDF model, hoặc sửa luồng train trong backend.
---

# Train từ DataRef

## Luồng Admin

1. Đăng nhập tại `/admin.html`
2. Chọn **nhiều** file JSON từ `src/DataRef/`
3. Bấm **Train**
4. Backend gộp `entries` → rebuild TF-IDF → lưu `src/data/model/`

## API

```
POST /api/admin/login     { "username", "password" }
GET  /api/admin/files     Liệt kê DataRef/*.json
POST /api/admin/train     { "files": ["minhlong.json", "..."] }
```

Header sau login: `Authorization: Bearer <token>`

## Kiểm tra sau train

- Response trả `entry_count`, `files`, `status`
- Thử chat câu hỏi liên quan nội dung trong file đã train
- Nếu không khớp: kiểm tra `question` trong JSON có gần cách khách hỏi không

## Code liên quan

- `src/backend/ingest/json_loader.py` — đọc & gộp JSON
- `src/backend/ai/vectorizer.py` — train & lưu model
- `src/backend/api/admin.py` — endpoint train
