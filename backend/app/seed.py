"""种子数据"""
import asyncio
import os
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.identity import IDENTITIES, PERSONNEL_TYPE_WAGES, personnel_daily_wage
from app.models import WorkType, AttendanceType, Employee, User


def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def seed_password(env_name: str, dev_default: str) -> str:
    password = os.getenv(env_name)
    if password:
        return password
    if settings.DEBUG:
        return dev_default
    raise RuntimeError(f"请通过环境变量 {env_name} 设置种子用户初始密码")


async def seed_work_types(db: AsyncSession):
    for name in IDENTITIES:
        exists = await db.execute(select(WorkType).where(WorkType.name == name))
        if not exists.scalar_one_or_none(): db.add(WorkType(name=name))
    await db.flush()
    print("Seeded work types")


async def seed_attendance_types(db: AsyncSession):
    for name, cat in [("项目出勤","project"),("院务工作","office"),("行政事务","office"),
                       ("临时任务","office"),("请假","leave"),("培训学习","office"),("其他","office")]:
        exists = await db.execute(select(AttendanceType).where(AttendanceType.name == name))
        if not exists.scalar_one_or_none(): db.add(AttendanceType(name=name, category=cat))
    await db.flush()
    print("Seeded attendance types")


async def seed_users(db: AsyncSession):
    # 管理员
    admin_emp = Employee(employee_code="EMP2025001", name="系统管理员", work_type="院长",
                         personnel_type="事业人员", department="地理信息院", position="院长",
                         daily_wage=personnel_daily_wage("事业人员"), status="在职")
    db.add(admin_emp); await db.flush()
    if not (await db.execute(select(User).where(User.username == "admin"))).scalar_one_or_none():
        db.add(User(username="admin", password_hash=hash_pw(seed_password("SEED_ADMIN_PASSWORD", "admin123")), role="院长", employee_id=admin_emp.id))

    # 项目经理 - 李赫
    lh_emp = Employee(employee_code="EMP2025002", name="李赫", work_type="项目经理",
                      personnel_type="事业人员", department="地理信息院", position="项目经理",
                      daily_wage=personnel_daily_wage("事业人员"), status="在职")
    db.add(lh_emp); await db.flush()
    if not (await db.execute(select(User).where(User.username == "lihe"))).scalar_one_or_none():
        db.add(User(username="lihe", password_hash=hash_pw(seed_password("SEED_LIHE_PASSWORD", "123456")), role="项目经理", employee_id=lh_emp.id))

    # 员工 - 宋英伦（事业人员）
    syl_emp = Employee(employee_code="EMP2025003", name="宋英伦", work_type="技术员",
                       personnel_type="事业人员", department="地理信息院", position="技术员",
                       daily_wage=personnel_daily_wage("事业人员"), status="在职")
    db.add(syl_emp); await db.flush()
    if not (await db.execute(select(User).where(User.username == "songyinglun"))).scalar_one_or_none():
        db.add(User(username="songyinglun", password_hash=hash_pw(seed_password("SEED_SONGYINGLUN_PASSWORD", "123456")), role="技术员", employee_id=syl_emp.id))

    # 员工 - 齐秀坤（事业人员）
    qxk_emp = Employee(employee_code="EMP2025004", name="齐秀坤", work_type="技术员",
                       personnel_type="事业人员", department="地理信息院", position="技术负责",
                       daily_wage=personnel_daily_wage("事业人员"), status="在职")
    db.add(qxk_emp); await db.flush()

    # 企业人员 - 测试
    ent_emp = Employee(employee_code="EMP2025005", name="企业员工1", work_type="技术员",
                       personnel_type="企业人员", department="地理信息院", position="技术员",
                       daily_wage=personnel_daily_wage("企业人员"), status="在职")
    db.add(ent_emp);
    await db.flush()

    print("Seeded users and employees")


async def main():
    async with async_session() as db:
        async with db.begin():
            await seed_work_types(db)
            await seed_attendance_types(db)
            await seed_users(db)
        await db.commit()
    print("Seed completed!")


if __name__ == "__main__":
    asyncio.run(main())
