---
name: convert-url-to-dataref
description: Chuyển URL website thành file DataRef JSON qua CLI scrape. Dùng khi cần tạo hoặc cập nhật dữ liệu train từ website, chạy tools.url_to_json, hoặc làm việc với DataRef từ nguồn web.
---

# Convert URL → DataRef JSON

## Khi nào dùng

- Cần tạo file mới trong `src/DataRef/` từ một website
- Cập nhật dữ liệu sau khi website thay đổi
- Sinh viên chuẩn bị dataset train lần đầu

## Lệnh CLI

Từ thư mục gốc project (đặt `PYTHONPATH=src`):

```bash
# Windows PowerShell
$env:PYTHONPATH = "src"
python -m tools.url_to_json <URL> --output src/DataRef/<ten-file>.json
```

Ví dụ:

```bash
$env:PYTHONPATH = "src"
python -m tools.url_to_json https://minhlongmoto.com/ --output src/DataRef/minhlong.json --max-pages 30
```

## Workflow

1. Chạy CLI với URL nguồn
2. Kiểm tra file output trong `src/DataRef/`
3. Mở JSON, xem `entries` có `question`/`answer` hợp lý
4. Sửa thủ công nếu cần (hoặc dùng skill `add-qa-entry`)
5. Commit file vào repo
6. Admin train qua web UI (skill `train-from-dataref`)

## Schema output

Xem `.cursor/rules/dataref-format.mdc` — mỗi entry cần `id`, `question`, `answer`.

## Lưu ý

- Công cụ này **độc lập** với web app; không cần đăng nhập
- Được dùng AI thị trường hỗ trợ sinh Q&A **chỉ trong** `src/tools/` nếu cần
- Không gọi LLM trong luồng chat/inference
