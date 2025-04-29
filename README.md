
# 사내 업무용 RAG 챗봇 설계 (pgvector + OpenSearch + MCP)
> 저장일: 2025-04-29

---

## 1. 목표

- **Vector DB**: PostgreSQL(pgvector)와 OpenSearch 모두 사용
- **MCP (Model Collaboration Protocol)** 기반: GPT-4o + Claude-3 활용
- **정확성 높은** + **약간의 창의성 있는** 사내 업무 지원 챗봇 구축
- **운영 시 정책**: LLM(OpenAI, Claude 등) 사용 시 데이터 및 질문/답변은 학습 불가 모드로 설정 (공개모드 테스트 후 적용)

---

## 2. 전체 아키텍처

```plaintext
[사용자 질문 입력]
    ↓
[질문 임베딩 변환]
    ↓
[벡터 검색]
    - OpenSearch (Dense+Sparse)
    - PostgreSQL(pgvector) (Dense)
    ↓
[MCP Retriever: 검색 결과 통합]
    ↓
[PostgreSQL: 원문 조회]
    ↓
[GPT-4o: 초안 생성]
[Claude-3: 검증 및 강화]
    ↓
[MCP Generator: 최종 답변 조합]
    ↓
[사용자 응답]
```

---

## 3. 데이터 흐름 요약

| 단계 | 설명 |
|:--|:--|
| 1 | 질문 임베딩 생성 |
| 2 | OpenSearch + pgvector 검색 |
| 3 | 검색 결과 병합 (Top-k 통합) |
| 4 | PostgreSQL에서 원문 조회 |
| 5 | GPT-4o로 초안 생성 |
| 6 | Claude-3로 검증 및 강화 |
| 7 | 최종 답변 제공 |

---

## 4. 주요 기술 스택

| 구분 | 기술 | 비고 |
|:--|:--|:--|
| Backend | FastAPI | 비동기 처리, 확장성 |
| DB | PostgreSQL + pgvector | 원문 저장, 벡터 저장 |
| Vector Search | OpenSearch | Dense+Sparse Hybrid 검색 |
| Embedding Model | OpenAI `text-embedding-3-small` | 벡터 임베딩 |
| Generator | GPT-4o, Claude-3 Opus | 답변 생성 및 강화 |
| 배포 | Docker Compose | 초기 빠른 구축 |

---

## 5. MCP 설계

### MCP Retriever
- OpenSearch + pgvector 결과 병합
- 중복 제거, 스코어 기반 정렬
- 하이브리드 가중치 조정 가능 (ex: Dense 0.7 / Sparse 0.3)

### MCP Generator
- GPT-4o: 초안 생성 (빠른 작성)
- Claude-3: 초안 검증 및 강화 (정확성 강화)
- Generator 결과 합성하여 최종 답변 결정

---

## 6. 모듈 설계

| 모듈 | 설명 |
|:--|:--|
| `retriever_opensearch.py` | OpenSearch 검색기 |
| `retriever_pgvector.py` | pgvector 검색기 |
| `mcp_retriever.py` | 검색 결과 통합 |
| `db_manager.py` | PostgreSQL 문서 관리 |
| `embedding_service.py` | 임베딩 생성기 |
| `generator_gpt.py` | GPT-4o 답변 생성 |
| `generator_claude.py` | Claude-3 검증 강화 |
| `mcp_generator.py` | 두 모델 답변 조합 |
| `api_server.py` | FastAPI API 서버 |

---

# ✅ 현재까지 저장된 상태
- 핵심 목표/구조/기술 선택/모듈까지 정리 완료
- 향후 코드 작성 및 MVP 개발로 확장 가능

---
