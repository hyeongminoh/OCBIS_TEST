import os
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from dotenv import load_dotenv

load_dotenv()

app = AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))

# ✅ @봇에게 멘션이 오면 반응
@app.event("app_mention")
async def handle_mention(body, say):
    user = body["event"]["user"]
    await say(f"안녕 <@{user}>! RAG 챗봇 작동 중이야 🤖")

async def main():
    handler = AsyncSocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    await handler.start_async()

# 👇 asyncio 루프에서 실행
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
