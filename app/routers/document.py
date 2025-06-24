from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String
from pgvector.sqlalchemy import Vector
from sqlalchemy import text
from app.core.database import Base
from app.core.database import get_db
from app.models.document import Document
from app.services.opensearch_client import client, index_name
from fastapi import Query
import os
import openai

router = APIRouter()

#mode로 조정
@router.post("/documents")
async def add_document(
    content: str,
    mode: str = Query("db", enum=["db", "os", "both"]),
    db: AsyncSession = Depends(get_db)
):
    # 1. GPT 임베딩
    response = openai.embeddings.create(
        input=content,
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding

    result = {"mode": mode}

    # 2. PostgreSQL 저장
    if mode in ("db", "both"):
        try:
            print("✅ PG 저장 시도")
            doc = Document(content=content, embedding=embedding)
            db.add(doc)
            await db.flush()
            print(f"✅ PG 저장 완료, doc_id = {doc.id}")
            doc_id = doc.id
            await db.commit()
            result["postgres_id"] = doc_id
        except Exception as e:
            await db.rollback()
            print("❌ PG 저장 실패:", e)

    # 3️⃣ OpenSearch 저장 (pg_id만!)
    if mode in ("os", "both"):
        body = {
            "embedding": embedding
        }
        if doc_id is not None:
            body["pg_id"] = doc_id

        client.index(index=index_name, body=body)
        result["opensearch"] = "stored"

    return result


@router.get("/search")
async def search(
    query: str,
    mode: str = Query("db", enum=["db", "os", "both"]),
    db: AsyncSession = Depends(get_db)
):
    # 1. GPT 임베딩 생성
    response = openai.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding
    results = {"mode": mode}

    # 2. PostgreSQL 검색
    if mode in ("db", "both"):
        embedding_str = ','.join(map(str, embedding))
        stmt = text(f"""
            SELECT id, content
            FROM documents
            ORDER BY embedding <-> ARRAY[{embedding_str}]::vector
            LIMIT 1
        """)
        result = await db.execute(stmt)
        row = result.fetchone()
        if row:
            results["postgresql"] = {"id": row.id, "content": row.content}

    # 3. OpenSearch 검색
    if mode in ("os", "both"):
        search_body = {
            "size": 1,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": embedding,
                        "k": 1
                    }
                }
            }
        }
        res = client.search(index=index_name, body=search_body)
        if res["hits"]["hits"]:
            doc = res["hits"]["hits"][0]["_source"]
            results["opensearch"] = {"content": doc["content"]}

    return results