import base64
import html
import random
import secrets
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.dependencies import create_access_token, get_current_user, hash_password, verify_password
from app.models import User
from app.schemas.auth import CaptchaResponse, ChangePasswordRequest, LoginRequest, TokenResponse, UserInfo

router = APIRouter(prefix="/api/auth", tags=["认证"])

CAPTCHA_TTL_SECONDS = 300
CAPTCHA_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_captcha_store: dict[str, tuple[str, float]] = {}


def _cleanup_captchas() -> None:
    now = time.time()
    expired = [key for key, (_, expires_at) in _captcha_store.items() if expires_at < now]
    for key in expired:
        _captcha_store.pop(key, None)


def _new_captcha_code() -> str:
    return "".join(secrets.choice(CAPTCHA_CHARS) for _ in range(4))


def _captcha_svg(code: str) -> str:
    random.seed()
    text_parts = []
    for index, char in enumerate(code):
        x = 22 + index * 26
        y = random.randint(34, 46)
        rotate = random.randint(-16, 16)
        color = random.choice(["#1d4ed8", "#047857", "#b45309", "#be123c", "#4338ca"])
        text_parts.append(
            f'<text x="{x}" y="{y}" transform="rotate({rotate} {x} {y})" '
            f'fill="{color}">{html.escape(char)}</text>'
        )
    noise = []
    for _ in range(6):
        x1, y1 = random.randint(4, 128), random.randint(8, 54)
        x2, y2 = random.randint(4, 128), random.randint(8, 54)
        noise.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            'stroke="rgba(31,41,55,.25)" stroke-width="1" />'
        )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="140" height="56" viewBox="0 0 140 56">'
        '<rect width="140" height="56" rx="8" fill="#f3f4f6" />'
        + "".join(noise)
        + '<g font-family="Arial, sans-serif" font-size="28" font-weight="700" '
        'letter-spacing="2">'
        + "".join(text_parts)
        + "</g></svg>"
    )
    encoded = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{encoded}"


def _verify_captcha(captcha_id: str, captcha_code: str) -> bool:
    _cleanup_captchas()
    stored = _captcha_store.pop(captcha_id, None)
    if not stored:
        return False
    expected, expires_at = stored
    if expires_at < time.time():
        return False
    return expected.lower() == captcha_code.strip().lower()


@router.get("/captcha", response_model=CaptchaResponse)
async def captcha():
    _cleanup_captchas()
    code = _new_captcha_code()
    captcha_id = str(uuid.uuid4())
    _captcha_store[captcha_id] = (code, time.time() + CAPTCHA_TTL_SECONDS)
    return CaptchaResponse(captcha_id=captcha_id, image=_captcha_svg(code))


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    if not _verify_captcha(req.captcha_id, req.captcha_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期")

    result = await db.execute(
        select(User).options(joinedload(User.employee)).where(User.username == req.username)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号已被禁用")

    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(
        access_token=token,
        id=user.id,
        username=user.username,
        role=user.role,
        employee_id=user.employee_id,
        employee_name=user.employee.name if user.employee else None,
    )


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        employee_id=current_user.employee_id,
        employee_name=current_user.employee.name if current_user.employee else None,
    )


@router.post("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if len(req.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码至少 6 位")
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
    current_user.password_hash = hash_password(req.new_password)
    await db.commit()
    return {"message": "密码修改成功"}
