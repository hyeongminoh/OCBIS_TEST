from fastapi import APIRouter
from app.services.opensearch_client import client
import openai
import os

router = APIRouter()

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
