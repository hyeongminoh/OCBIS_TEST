# app/services/opensearch_client.py
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),  # 기본 계정
    use_ssl=False,
    verify_certs=False
)

# ✅ 인덱스 존재 여부 확인 후 없으면 생성
index_name = "documents"
if not client.indices.exists(index=index_name):
    client.indices.create(index=index_name)