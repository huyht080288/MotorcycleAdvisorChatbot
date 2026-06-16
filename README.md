# Motorcycle Advisor Chatbot

Chatbot tư vấn khách hàng cho cửa hàng bán xe máy (Minh Long Motor). AI dùng **TF-IDF + Cosine Similarity** (tự triển khai, không dùng LLM thương mại khi trả lời).

**Nhóm 12** — Môn Phát Triển Hệ Thống Thông Minh

## Yêu cầu hệ thống

| Thành phần | Phiên bản tối thiểu |
|------------|---------------------|
| Python | 3.11+ |
| pip | đi kèm Python |
| Trình duyệt | Chrome, Edge, Firefox (bản mới) |
| Hệ điều hành | Windows 10/11, Linux, macOS |

Kiểm tra Python:

```powershell
python --version
```

## Tính năng

- Trang chủ cửa hàng xe máy + widget chat AI (cố định góc dưới phải)
- Chat khách (guest) — tiếng Việt
- Admin đăng nhập → chọn **nhiều** file `DataRef/*.json` → **Train**
- CLI chuyển URL website → file JSON: `python -m tools.url_to_json`

---

## Hướng dẫn chạy source (Windows / PowerShell)

### Bước 1 — Mở thư mục dự án

```powershell
cd c:\D\Tret\HK7\HTTM
```

> Đổi đường dẫn nếu bạn clone repo ở vị trí khác.

### Bước 2 — Tạo virtual environment (chỉ lần đầu)

```powershell
python -m venv .venv
```

### Bước 3 — Kích hoạt virtual environment

```powershell
.venv\Scripts\activate
```

Khi thành công, đầu dòng lệnh hiện `(.venv)`.

### Bước 4 — Cài thư viện (chỉ lần đầu hoặc khi đổi `requirements.txt`)

```powershell
pip install -r requirements.txt
```

### Bước 5 — Tạo file cấu hình `.env` (chỉ lần đầu)

```powershell
copy .env.example .env
```

Chỉnh `.env` nếu cần (mật khẩu admin, ngưỡng AI):

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
SECRET_KEY=doi-secret-key-trong-production
CONFIDENCE_THRESHOLD=0.25
```

### Bước 6 — Chạy server

```powershell
uvicorn backend.main:app --reload --port 8000
```

Thấy dòng sau là server đã chạy:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Lệnh rút gọn** (không cần `activate`):

```powershell
.venv\Scripts\uvicorn backend.main:app --reload --port 8000
```

### Bước 7 — Mở trình duyệt

| Trang | URL |
|-------|-----|
| Trang chủ + chat | http://localhost:8000 |
| Quản trị (Train AI) | http://localhost:8000/admin.html |
| API docs (Swagger) | http://localhost:8000/docs |

### Bước 8 — Train AI lần đầu (bắt buộc trước khi chat)

1. Vào http://localhost:8000/admin.html
2. Đăng nhập: `admin` / `admin123`
3. Chọn một hoặc nhiều file JSON (vd. `minhlongmoto-com.json`)
4. Bấm **Train**
5. Quay lại http://localhost:8000 và thử chat

### Dừng server

Trong terminal đang chạy server, nhấn `Ctrl + C`.

---

## Hướng dẫn chạy source (Linux / macOS)

```bash
cd /path/to/motorcycle-advisor-chatbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.main:app --reload --port 8000
```

---

## Tạo dữ liệu từ website (CLI)

Scrape nội dung website thành file JSON trong `DataRef/`:

```powershell
.venv\Scripts\activate
python -m tools.url_to_json https://minhlongmoto.com/ --output DataRef/minhlongmoto-com.json --max-pages 30
```

| Tham số | Mô tả |
|---------|--------|
| `url` | URL website nguồn |
| `--output`, `-o` | Đường dẫn file JSON output |
| `--max-pages` | Số trang tối đa crawl (mặc định: 20) |

Sau khi scrape → vào Admin → chọn file mới → **Train** lại.

---

## Xử lý lỗi thường gặp

### Lỗi `WinError 10013` khi chạy port 8000

Port 8000 đang bị chiếm bởi process khác (thường là server cũ).

**Cách 1 — Tắt process đang giữ port:**

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

**Cách 2 — Đổi sang port khác:**

```powershell
uvicorn backend.main:app --reload --port 8080
```

Truy cập: http://localhost:8080

### Chatbot trả lời "Hệ thống chưa được train"

→ Vào Admin, chọn file `DataRef/*.json` và bấm **Train**.

### `pip` / `uvicorn` không nhận lệnh

→ Chưa activate venv hoặc chưa cài dependencies:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## API nhanh (test bằng curl / PowerShell)

**Kiểm tra server:**

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

**Chat:**

```powershell
Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/chat `
  -ContentType "application/json" `
  -Body '{"message":"Giá xe Vario 125"}'
```

**Đăng nhập admin:**

```powershell
$login = Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/admin/login `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"admin123"}'
$token = $login.token
```

**Train:**

```powershell
Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/admin/train `
  -ContentType "application/json" `
  -Headers @{ Authorization = "Bearer $token" } `
  -Body '{"files":["minhlongmoto-com.json"]}'
```

---

## Cấu trúc thư mục

```
motorcycle-advisor-chatbot/
├── DataRef/              # Dữ liệu train (JSON)
├── tools/                # CLI url → JSON
├── backend/              # FastAPI + TF-IDF engine
│   ├── api/              # chat, admin, site
│   └── ai/               # preprocessor, vectorizer
├── frontend/             # Giao diện web
├── data/model/           # Model sau khi train (*.joblib)
├── Report/               # Báo cáo đồ án
├── .env.example          # Mẫu cấu hình
└── requirements.txt      # Python dependencies
```

---

## Admin mặc định

| Trường | Giá trị mặc định |
|--------|------------------|
| Tài khoản | `admin` |
| Mật khẩu | `admin123` |

Đổi trong file `.env` trước khi deploy thực tế.

---

## Thuật toán AI (tóm tắt)

1. Gộp `entries` từ các file JSON admin chọn
2. Vector hóa **TF-IDF** trên `question + " " + answer`
3. Khi chat: **cosine similarity** → trả lời entry khớp nhất
4. Ngưỡng tin cậy mặc định: `0.25` (cấu hình trong `.env`)

Chi tiết: xem `Report/NHOM12_PHATTRIENHETHONGTHONGMINH.md`

---

## Quy trình làm việc đề xuất

```text
1. python -m tools.url_to_json <URL>     → tạo DataRef/*.json
2. uvicorn backend.main:app ...          → chạy server
3. Admin → Train (chọn file JSON)        → build model
4. Trang chủ → chat thử                  → kiểm tra kết quả
```
# MotorcycleAdvisorChatbot
