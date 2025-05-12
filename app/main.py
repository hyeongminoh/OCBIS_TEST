from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import slack
from app.routers import document
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

app = FastAPI()

app.include_router(slack.router)
app.include_router(document.router)

# CORS 설정 (테스트용 전체 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FastAPI + PostgreSQL + pgvector 연결 테스트!"}

# ✅ DB 연결 확인용 API
@app.get("/ping-db")
async def ping_db(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        return {"db_status": result.scalar() == 1}
    except Exception as e:
        return {"db_status": False, "error": str(e)}