
# 📄 사내 업무용 RAG 챗봇 - API 명세

---

## 1. 문서 관리 API

### 1.1 문서 등록
- **POST /documents/**
- **설명**: 새 문서를 등록하고, 임베딩을 생성하여 PostgreSQL + OpenSearch에 저장
- **요청 Body**
```json
{
  "title": "문서 제목",
  "content": "문서 본문",
  "category": "카테고리 (선택)"
}
```
- **응답**
```json
{
  "document_id": 123
}
```

---

### 1.2 문서 조회
- **GET /documents/{id}**
- **설명**: 특정 문서(id) 조회
- **응답**
```json
{
  "id": 123,
  "title": "문서 제목",
  "content": "문서 본문",
  "category": "카테고리",
  "created_at": "2025-04-29T10:00:00",
  "updated_at": "2025-04-29T10:00:00"
}
```

---

### 1.3 문서 수정
- **PUT /documents/{id}**
- **설명**: 문서를 수정하고 임베딩도 재생성
- **요청 Body**
```json
{
  "title": "수정된 제목",
  "content": "수정된 본문",
  "category": "수정된 카테고리"
}
```

---

### 1.4 문서 삭제
- **DELETE /documents/{id}**
- **설명**: 문서를 삭제하고 OpenSearch에서도 제거

---

## 2. 검색 및 답변 API

### 2.1 질문 검색 (RAG)
- **POST /search/**
- **설명**: 사용자 질문을 임베딩하여 유사 문서를 검색
- **요청 Body**
```json
{
  "question": "사내 복리후생 제도 알려줘"
}
```
- **응답**
```json
{
  "results": [
    {
      "document_id": 123,
      "title": "복리후생 제도",
      "content_snippet": "우리 회사는 다양한 복지제도를 운영합니다..."
    },
    ...
  ]
}
```

---

### 2.2 답변 생성 (MCP 기반)
- **POST /generate-answer/**
- **설명**: 검색된 문서를 바탕으로 GPT-4o + Claude-3를 활용해 최종 답변 생성
- **요청 Body**
```json
{
  "question": "사내 복리후생 제도 알려줘",
  "document_ids": [123, 124, 125]
}
```
- **응답**
```json
{
  "answer": "우리 회사는 다양한 복리후생 제도를 운영하고 있습니다. 예를 들면..."
}
```

---

## 3. Slack 연동 API

### 3.1 Slack 이벤트 수신
- **POST /slack/events**
- **설명**: Slack 이벤트를 수신하여 질문을 처리

**Slack Event 예시**
```json
{
  "event": {
    "type": "message",
    "user": "U12345678",
    "text": "휴가 정책 알려줘",
    "channel": "C12345678",
    "ts": "1624398420.000200"
  }
}
```

---

# ✅ 요약
- 문서 저장/검색/답변/Slack 연동 모두 API로 구성
- FastAPI + PostgreSQL + OpenSearch + OpenAI/Claude 호출 통합
- 모든 API는 비동기(Async) 처리 예정

---
