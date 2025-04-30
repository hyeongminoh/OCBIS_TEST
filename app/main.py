from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import slack

app = FastAPI()

app.include_router(slack.router)

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
    return {"message": "🚀 Hello from your RAG chatbot API!"}
