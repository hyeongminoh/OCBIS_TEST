# app/services/opensearch_client.py
import os
from opensearchpy import OpenSearch


client = OpenSearch(
    hosts=[{"host": os.getenv("OPENSEARCH_HOST", "localhost"), "port": int(os.getenv("OPENSEARCH_PORT", 9200))}],
    use_ssl=False,
    verify_certs=False,
    http_auth=os.getenv("OPENSEARCH_AUTH", None)  # 예: "admin:admin" 형태
)


# ✅ 인덱스 존재 여부 확인 후 없으면 생성
index_name = "documents"
if not client.indices.exists(index=index_name):
    client.indices.create(index=index_name)