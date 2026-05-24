from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.dependencies import create_access_token, get_current_user, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
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
