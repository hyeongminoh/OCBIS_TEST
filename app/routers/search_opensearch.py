from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Base
from app.core.database import get_db
from app.models.document import Document
from app.services.opensearch_client import client, index_name
import openai
import os

router = APIRouter()

#opensearch에만 저장
@router.post("/documents/opensearch")
async def add_to_opensearch(content: str):
    # OpenAI 임베딩 생성
    response = openai.embeddings.create(
        input=content,
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding

    # OpenSearch에 문서 삽입
    doc = {
        "content": content,
        "embedding": embedding
    }

    client.index(index="documents", body=doc)
    return {"status": "inserted to opensearch"}

@router.post("/documents/both")
async def add_to_both(content: str, db: AsyncSession = Depends(get_db)):
    # 1️⃣ OpenAI 임베딩 생성
    response = openai.embeddings.create(
        input=content,
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding

    # 2️⃣ PostgreSQL 저장
    doc = Document(content=content, embedding=embedding)
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # 3️⃣ OpenSearch 저장
    client.index(
        index=index_name,
        body={
            "id": doc.id,
            "content": content,
            "embedding": embedding
        }
    )

    return {
        "status": "inserted to both postgreSQL + opensearch",
        "doc_id": doc.id
    }

@router.get("/documents/opensearch/search")
async def search_in_opensearch(query: str):
    # OpenAI 임베딩 생성
    response = openai.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding

    # OpenSearch 벡터 검색 (KNN)
    search_body = {
        "size": 3,
        "query": {
            "knn": {
                "embedding": {
                    "vector": embedding,
                    "k": 3
                }
            }
        }
    }

    result = client.search(index="documents", body=search_body)
    return result["hits"]["hits"]
