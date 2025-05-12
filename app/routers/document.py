from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String
from pgvector.sqlalchemy import Vector
from sqlalchemy import text
from app.core.database import Base
from app.core.database import get_db
from app.models.document import Document
from openai import OpenAI # OpenAI API 사용
import os

router = APIRouter()

@router.post("/documents")
async def add_document(content: str, db: AsyncSession = Depends(get_db)):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # 1️⃣ OpenAI 임베딩 생성
    response = client.embeddings.create(
        input=content,
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding  # 임베딩 벡터 추출

    # 2️⃣ DB에 저장
    doc = Document(content=content, embedding=embedding)
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    return {"id": doc.id, "content": doc.content}


@router.get("/documents/search")
async def search_document(query_embedding: list[float], db: AsyncSession = Depends(get_db)):
    # pgvector 유사도 검색 (Euclidean, Cosine → "<->", "<=>", "<#>" 연산자 사용 가능)
    embedding_str = ','.join(map(str, query_embedding))
    stmt = text(f"""
        SELECT id, content
        FROM documents
        ORDER BY embedding <-> ARRAY[{embedding_str}]::vector
        LIMIT 1
    """)
    result = await db.execute(stmt)
    row = result.fetchone()
    if row:
        return {"id": row.id, "content": row.content}
    return {"message": "No matching document found."}