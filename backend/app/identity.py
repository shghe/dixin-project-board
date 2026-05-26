IDENTITIES = ("院长", "副院长", "综合员", "司机", "项目经理", "技术员")

PERSONNEL_TYPE_WAGES: dict[str, float] = {
    "事业人员": 650,
    "企业人员": 500,
    "派遣人员": 380,
}

LEGACY_IDENTITY_MAP = {
    "director": "院长",
    "manager": "项目经理",
    "finance": "综合员",
    "employee": "技术员",
    "项目负责": "项目经理",
    "测量员": "技术员",
    "绘图员": "技术员",
    "内业": "综合员",
}

ROLE_GROUPS = {
    "director": ("院长", "副院长"),
    "院长": ("院长", "副院长"),
    "副院长": ("副院长",),
    "manager": ("项目经理",),
    "项目经理": ("项目经理",),
    "finance": ("综合员",),
    "综合员": ("综合员",),
    "employee": ("司机", "技术员"),
    "司机": ("司机",),
    "技术员": ("技术员",),
}


def normalize_identity(value: str | None, default: str = "技术员") -> str:
    identity = (value or "").strip()
    if not identity:
        return default
    return LEGACY_IDENTITY_MAP.get(identity, identity if identity in IDENTITIES else default)


def personnel_daily_wage(personnel_type: str | None, wages: dict[str, float] | None = None) -> float:
    if wages is None:
        wages = PERSONNEL_TYPE_WAGES
    return wages.get((personnel_type or "").strip(), 488)


async def load_personnel_wages(db) -> dict[str, float]:
    from sqlalchemy import select
    from app.models.system_config import SystemConfig

    result = await db.execute(select(SystemConfig).where(SystemConfig.key.like("wage_%")))
    wages = dict(PERSONNEL_TYPE_WAGES)
    for row in result.scalars().all():
        personnel_type = row.key.removeprefix("wage_")
        try:
            wages[personnel_type] = float(row.value)
        except (ValueError, TypeError):
            continue
    return wages


def role_matches(user_role: str | None, roles: tuple[str, ...]) -> bool:
    user_identity = normalize_identity(user_role)
    allowed: set[str] = set()
    for role in roles:
        group = ROLE_GROUPS.get(role)
        if group:
            allowed.update(group)
        else:
            allowed.add(normalize_identity(role))
    return user_identity in allowed
