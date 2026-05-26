from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, employees, projects, execution, reports, personal_work, budget_v2, users, wage_config

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(budget_v2.router)  # 必须在 projects 之前，避免 /budget/summary 被 /budget/{item_id} 捕获
app.include_router(projects.router)
app.include_router(execution.router)
app.include_router(reports.router)
app.include_router(personal_work.router)
app.include_router(users.router)
app.include_router(wage_config.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
