from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.dependencies import get_current_user, require_role, hash_password
from app.models import User, Employee
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/api/users", tags=["账号管理"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("director")),
):
    result = await db.execute(
        select(User).options(joinedload(User.employee)).order_by(User.created_at.desc())
    )
    users = result.unique().scalars().all()
    return [
        UserResponse(
            id=u.id,
            username=u.username,
            role=u.role,
            employee_id=u.employee_id,
            employee_name=u.employee.name if u.employee else None,
            is_active=u.is_active,
            created_at=u.created_at,
        )
        for u in users
    ]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("director")),
):
    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role,
        employee_id=data.employee_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    result = await db.execute(
        select(User).options(joinedload(User.employee)).where(User.id == user.id)
    )
    u = result.unique().scalar_one()
    return UserResponse(
        id=u.id,
        username=u.username,
        role=u.role,
        employee_id=u.employee_id,
        employee_name=u.employee.name if u.employee else None,
        is_active=u.is_active,
        created_at=u.created_at,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("director")),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if data.password is not None:
        user.password_hash = hash_password(data.password)
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    await db.commit()
    await db.refresh(user)
    result = await db.execute(
        select(User).options(joinedload(User.employee)).where(User.id == user.id)
    )
    u = result.unique().scalar_one()
    return UserResponse(
        id=u.id,
        username=u.username,
        role=u.role,
        employee_id=u.employee_id,
        employee_name=u.employee.name if u.employee else None,
        is_active=u.is_active,
        created_at=u.created_at,
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("director")),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    await db.delete(user)
    await db.commit()
    return {"message": "删除成功"}
