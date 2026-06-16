# Motorcycle Advisor Chatbot

Customer advisory chatbot for a motorcycle store (Minh Long Motor). The AI uses **TF-IDF + Cosine Similarity** (self-implemented; no commercial LLM is used when answering).

**Group 12** — Intelligent Systems Development

## System Requirements

| Component | Minimum Version |
|-----------|-----------------|
| Python | 3.11+ |
| pip | Bundled with Python |
| Browser | Chrome, Edge, Firefox (recent) |
| OS | Windows 10/11, Linux, macOS |

```powershell
python --version
```

## Features

- Motorcycle store homepage + AI chat widget (fixed at bottom-right)
- Guest chat — Vietnamese UI
- Admin login → select multiple JSON files → **Train**
- CLI to scrape a website URL into training data

---

## Quick Start

From the project root directory:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r src/requirements.txt
copy src\.env.example src\.env
.\run.ps1
```

Then open http://localhost:8000/admin.html → login `admin` / `admin123` → select `minhlongmoto-com.json` → **Train** → chat at http://localhost:8000

---

## Running with Docker

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose).

### Step 1 — Prepare config

```powershell
copy src\.env.example src\.env
```

### Step 2 — Build and start

```powershell
docker compose up --build -d
```

| Service | Role | Host access |
|---------|------|-------------|
| `frontend` | Nginx serves UI, proxies `/api` | http://localhost:8081 |
| `backend` | FastAPI + TF-IDF engine | internal only (port 8000) |

### Step 3 — Train and use

1. http://localhost:8081/admin.html → login `admin` / `admin123`
2. Select JSON file(s) → **Train**
3. http://localhost:8081 → chat

| Page | URL |
|------|-----|
| Homepage + chat | http://localhost:8081 |
| Admin | http://localhost:8081/admin.html |
| API docs | http://localhost:8081/docs |

### Useful commands

```powershell
docker compose logs -f          # view logs
docker compose ps               # container status
docker compose down             # stop and remove containers
docker compose up --build -d    # rebuild after code changes
```

**Persisted data** (mounted from host):

- `src/DataRef/` — training JSON files
- `src/data/model/` — trained model after Admin → Train

---

## Running the Source (Windows / PowerShell)

### Step 1 — Open the project directory

```powershell
cd motorcycle-advisor-chatbot
```

Use the folder where you cloned or extracted this repository.

### Step 2 — Create a virtual environment (first time only)

```powershell
python -m venv .venv
```

### Step 3 — Activate the virtual environment

```powershell
.venv\Scripts\activate
```

On success, the prompt shows `(.venv)`.

### Step 4 — Install dependencies

```powershell
pip install -r src/requirements.txt
```

### Step 5 — Create config file (first time only)

```powershell
copy src\.env.example src\.env
```

Edit `src/.env` if needed:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
SECRET_KEY=change-this-secret-in-production
CONFIDENCE_THRESHOLD=0.25
```

### Step 6 — Start the server

**Option A — helper script (recommended):**

```powershell
.\run.ps1
```

**Option B — manual:**

```powershell
$env:PYTHONPATH = "src"
uvicorn backend.main:app --reload --port 8000
```

**Option C — CMD:**

```cmd
run.bat
```

The server is running when you see:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 7 — Open in a browser

| Page | URL |
|------|-----|
| Homepage + chat | http://localhost:8000 |
| Admin (Train AI) | http://localhost:8000/admin.html |
| API docs (Swagger) | http://localhost:8000/docs |

### Step 8 — Train the AI (required before chatting)

1. Open http://localhost:8000/admin.html
2. Log in: `admin` / `admin123`
3. Select one or more JSON files (e.g. `minhlongmoto-com.json`)
4. Click **Train**
5. Open http://localhost:8000 and try chatting

### Stop the server

Press `Ctrl + C` in the terminal running the server.

> `run.ps1` / `run.bat` set `PYTHONPATH=src` and start Uvicorn. They are optional shortcuts — the manual commands above work the same way.

---

## Running the Source (Linux / macOS)

```bash
cd motorcycle-advisor-chatbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
cp src/.env.example src/.env
export PYTHONPATH=src
uvicorn backend.main:app --reload --port 8000
```

---

## Generate Data from a Website (CLI)

From the project root, with `PYTHONPATH=src`:

```powershell
$env:PYTHONPATH = "src"
python -m tools.url_to_json https://minhlongmoto.com/ --max-pages 30
```

Output is saved to `src/DataRef/` by default. To set a custom file:

```powershell
$env:PYTHONPATH = "src"
python -m tools.url_to_json https://minhlongmoto.com/ -o src/DataRef/minhlongmoto-com.json --max-pages 30
```

| Parameter | Description |
|-----------|-------------|
| `url` | Source website URL |
| `--output`, `-o` | Output JSON path (optional) |
| `--max-pages` | Maximum pages to crawl (default: 20) |

After scraping → Admin → select the new file → **Train**.

---

## Troubleshooting

### `WinError 10013` on port 8000

Port 8000 is already in use (often a previous server instance).

**Kill the process on port 8000:**

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

**Or use another port:**

```powershell
$env:PYTHONPATH = "src"
uvicorn backend.main:app --reload --port 8080
```

Open http://localhost:8080

### Chatbot says the system is not trained

→ Admin → select JSON file(s) → **Train**.

### `pip` or `uvicorn` not found

```powershell
.venv\Scripts\activate
pip install -r src/requirements.txt
```

---

## Quick API Tests (PowerShell)

```powershell
Invoke-RestMethod http://localhost:8000/api/health

Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/chat `
  -ContentType "application/json" `
  -Body '{"message":"Giá xe Vario 125"}'

$login = Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/admin/login `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"admin123"}'

Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/admin/train `
  -ContentType "application/json" `
  -Headers @{ Authorization = "Bearer $($login.token)" } `
  -Body '{"files":["minhlongmoto-com.json"]}'
```

---

## Project Structure

All application source code and config live under `src/`:

```
motorcycle-advisor-chatbot/
├── docker/
│   ├── backend/Dockerfile   # FastAPI image
│   └── frontend/            # Nginx image + nginx.conf
├── src/
│   ├── backend/          # FastAPI + TF-IDF engine
│   ├── frontend/         # Web UI
│   ├── tools/            # CLI url → JSON
│   ├── DataRef/          # Training data (JSON)
│   ├── data/model/       # Trained model (*.joblib)
│   ├── .env.example      # Config template
│   └── requirements.txt
├── docker-compose.yml    # Run backend + frontend (port 8081)
├── Report/               # Project report
├── run.ps1               # Start server (PowerShell)
├── run.bat               # Start server (CMD)
└── .venv/                # Virtual environment (local, not committed)
```

---

## Default Admin Credentials

| Field | Default |
|-------|---------|
| Username | `admin` |
| Password | `admin123` |

Change these in `src/.env` before production use.

---

## AI Algorithm (Summary)

1. Merge `entries` from JSON files selected by admin
2. **TF-IDF** vectorization on `question + " " + answer`
3. On chat: **cosine similarity** → return the best-matching entry
4. Default confidence threshold: `0.25` (`CONFIDENCE_THRESHOLD` in `src/.env`)

Details: `Report/NHOM12_PHATTRIENHETHONGTHONGMINH.md`

---

## Suggested Workflow

**Local development:**

```text
1. PYTHONPATH=src  python -m tools.url_to_json <URL>  →  src/DataRef/*.json
2. .\run.ps1                                         →  start server
3. Admin → Train                                     →  build model
4. Homepage → chat                                   →  verify results
```

**Docker:**

```text
1. copy src/.env.example → src/.env
2. docker compose up --build -d                      →  http://localhost:8081
3. Admin → Train
4. Homepage → chat
```
