from pathlib import Path

# Application root: src/
SRC_DIR = Path(__file__).resolve().parents[1]

DATAREF_DIR = SRC_DIR / "DataRef"
MODEL_DIR = SRC_DIR / "data" / "model"
FRONTEND_DIR = SRC_DIR / "frontend"
ENV_FILE = SRC_DIR / ".env"
