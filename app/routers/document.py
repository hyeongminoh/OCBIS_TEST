from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import VECTOR
from sqlalchemy import text
from app.database import Base
from app.database import get_db
from app.models.document import Document
import openai # OpenAI API 사용

router = APIRouter()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    embedding = Column(VECTOR(1536))  # 차원 수 맞게

@router.post("/documents")
async def add_document(content: str, db: AsyncSession = Depends(get_db)):
    # 1️⃣ OpenAI 임베딩 생성
    response = openai.Embedding.create(
        input=content,
        model="text-embedding-ada-002"
    )
    embedding = response["data"][0]["embedding"]  # 임베딩 벡터 추출

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