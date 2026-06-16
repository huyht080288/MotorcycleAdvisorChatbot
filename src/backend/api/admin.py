import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from backend.ai.vectorizer import model
from backend.ingest.json_loader import list_dataref_files, load_multiple_files

router = APIRouter(prefix="/api/admin", tags=["admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))


class LoginRequest(BaseModel):
    username: str
    password: str


class TrainRequest(BaseModel):
    files: list[str]


def create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=8)
    return jwt.encode(
        {"sub": username, "role": "admin", "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verify_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Chưa đăng nhập")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền")
        return payload.get("sub", "")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ")


@router.post("/login")
def login(body: LoginRequest) -> dict:
    if body.username != ADMIN_USERNAME or body.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai tài khoản hoặc mật khẩu")
    return {"token": create_token(body.username), "role": "admin"}


@router.get("/files")
def get_files(_: str = Depends(verify_admin)) -> dict:
    return {"files": list_dataref_files()}


@router.post("/train")
def train(body: TrainRequest, _: str = Depends(verify_admin)) -> dict:
    if not body.files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chọn ít nhất một file JSON")

    invalid = [f for f in body.files if not f.endswith(".json")]
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File không hợp lệ: {', '.join(invalid)}",
        )

    try:
        entries = load_multiple_files(body.files)
        count = model.train(entries, threshold=THRESHOLD)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "status": "ok",
        "entry_count": count,
        "files": body.files,
        "message": f"Đã train thành công {count} mục từ {len(body.files)} file.",
    }


@router.get("/status")
def get_status(_: str = Depends(verify_admin)) -> dict:
    return {
        "trained": model.is_ready(),
        "entry_count": len(model.entries) if model.entries else 0,
    }
