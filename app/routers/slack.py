from fastapi import APIRouter, Request
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp
import os
from dotenv import load_dotenv

load_dotenv()

slack_app = AsyncApp(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

# 📌 이벤트 핸들러 등록
@slack_app.event("app_mention")
async def handle_mention(body, say):
    user = body["event"]["user"]
    await say(f"<@{user}> 안녕! 슬랙에서 잘 작동하고 있어 🚀")

router = APIRouter()
handler = AsyncSlackRequestHandler(slack_app)

@router.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)
