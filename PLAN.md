# PLAN.md - 7-Day Production RAG Agent with Google ADK

## Context

Chuẩn bị onboard AI Engineer @ FPT Software. Build 1 project end-to-end từ zero:
**Google ADK Agent + RAG + Qdrant + FastAPI + Docker + pytest + CI/CD**

- Thời gian: 7 ngày x 3-4h/ngày (~24h total)
- Level hiện tại: PoC dev (đã build RAG với Langflow + Milvus, nhưng chưa production-ready)
- Domain: Enterprise Knowledge Assistant
- Mục tiêu: có muscle memory thật + 1 repo show được tech lead ngày đầu

---

## Project Structure (Target cuối tuần)

```
prod-agent-adk/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions: lint + test + docker build
├── src/
│   ├── __init__.py
│   ├── app.py                     # FastAPI entrypoint
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent.py               # ADK Agent definition
│   │   ├── tools.py               # Custom tools (RAG search)
│   │   ├── prompt.py              # System prompts
│   │   └── config.py              # Settings via pydantic-settings
│   └── rag/
│       ├── __init__.py
│       ├── ingest.py              # Document chunking + embedding + upsert Qdrant
│       ├── retriever.py           # Qdrant search wrapper
│       └── embeddings.py          # Embedding model config
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Shared fixtures
│   ├── test_ingest.py             # Unit test chunking
│   ├── test_tools.py              # Unit test agent tools
│   ├── test_app.py                # API endpoint tests
│   └── evals/
│       └── knowledge_qa.test.json # ADK eval test cases
├── scripts/
│   └── ingest_docs.py             # CLI script nạp tài liệu
├── docs/                           # Sample documents để demo
│   └── company_policy.md
├── Dockerfile
├── docker-compose.yml              # app + qdrant
├── .dockerignore
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

---

## Day 1 (3-4h): Project Skeleton + ADK Hello World

### Mục tiêu: Có 1 ADK agent chạy được, project structure professional

---

### Bước 1.1: Cài đặt tools cần thiết (15 phút)

```bash
# Cài uv (Python package manager hiện đại, thay pip/poetry)
# Windows PowerShell:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify
uv --version

# Cài Docker Desktop (nếu chưa có)
# Download: https://www.docker.com/products/docker-desktop/
# Sau khi cài, verify:
docker --version
docker compose version
```

### Bước 1.2: Init project (20 phút)

```bash
cd d:/Coding/Projects/prod-agent-adk

# Init Python project với uv
uv init --name prod-agent-adk --python 3.11

# Tạo structure
mkdir -p src/agent src/rag tests/evals scripts docs .github/workflows

# Tạo __init__.py files
touch src/__init__.py src/agent/__init__.py src/rag/__init__.py tests/__init__.py
```

**Tạo file `.gitignore`:**
```
__pycache__/
*.pyc
.env
.venv/
*.egg-info/
dist/
build/
.pytest_cache/
.ruff_cache/
```

**Tạo file `.env.example`:**
```env
GOOGLE_API_KEY=your-gemini-api-key-here
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=knowledge_base
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

### Bước 1.3: Cài dependencies (10 phút)

```bash
# Core dependencies
uv add google-adk qdrant-client fastembed pydantic-settings python-dotenv

# Dev tools
uv add --dev pytest pytest-asyncio ruff httpx
```

> **Giải thích dependencies:**
> - `google-adk`: Google Agent Development Kit - framework chính xây agent
> - `qdrant-client`: client cho Qdrant vector database
> - `fastembed`: lightweight embedding model (chạy local, không cần API key)
> - `pydantic-settings`: quản lý config qua .env file
> - `pytest`: testing framework chuẩn Python
> - `ruff`: linter + formatter siêu nhanh (thay flake8 + black + isort)
> - `httpx`: async HTTP client, dùng để test FastAPI endpoints

### Bước 1.4: ADK Hello World Agent (45 phút)

**File `src/agent/__init__.py`:**
```python
from .agent import agent

__all__ = ["agent"]
```

**File `src/agent/agent.py`:**
```python
from google.adk import Agent

agent = Agent(
    model="gemini-2.0-flash",
    name="knowledge_assistant",
    description="Enterprise knowledge assistant that helps employees find information.",
    instruction="""You are a helpful enterprise knowledge assistant.

    Your role:
    - Answer questions about company policies, procedures, and knowledge base
    - Be concise and accurate
    - If you don't know something, say so clearly
    - Always cite the source when using retrieved information
    """,
)
```

**Test chạy agent:**
```bash
# 1. Tạo file .env (copy từ .env.example, điền GOOGLE_API_KEY)
cp .env.example .env
# Edit .env → điền API key từ https://aistudio.google.com/apikey

# 2. Chạy ADK web UI
uv run adk web src
# Mở browser: http://localhost:8000
# Chọn agent "knowledge_assistant" → chat thử
```

> **Lưu ý:** `adk web src` nghĩa là ADK sẽ scan folder `src/` tìm agent.
> ADK tìm agent qua `__init__.py` exports. Nếu `src/agent/__init__.py` export `agent`,
> ADK sẽ tự động detect.

### Bước 1.5: Git first commit + push GitHub (15 phút)

```bash
# First commit
git add .
git commit -m "feat: init project structure + ADK hello world agent"

# Tạo repo trên GitHub
# Option A: dùng gh CLI (nếu đã cài)
gh repo create prod-agent-adk --public --source=. --push

# Option B: manual
# 1. Vào github.com → New repository → tên "prod-agent-adk"
# 2. Chạy:
git remote add origin https://github.com/YOUR_USERNAME/prod-agent-adk.git
git branch -M main
git push -u origin main
```

### ✅ Checkpoint Day 1:
- [ ] `uv run adk web src` chạy được, chat được với agent trên browser
- [ ] Repo trên GitHub với đầy đủ structure
- [ ] `.env.example` có nhưng `.env` KHÔNG bị commit (check .gitignore)
- [ ] Hiểu: pyproject.toml là gì, uv làm gì, ADK agent anatomy (model + name + instruction)

---

## Day 2 (3-4h): RAG Pipeline - Qdrant + Embedding + Retrieval

### Mục tiêu: Agent search knowledge từ Qdrant, trả lời dựa trên documents thật

---

### Bước 2.1: Chạy Qdrant bằng Docker (10 phút)

**Tạo file `docker-compose.yml`** (tạm thời chỉ có Qdrant, sẽ thêm app ở Day 5):
```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"   # REST API
      - "6334:6334"   # gRPC
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  qdrant_data:
```

```bash
# Chạy Qdrant
docker compose up qdrant -d

# Verify: mở http://localhost:6333/dashboard trong browser
# Nếu thấy Qdrant dashboard → OK
```

### Bước 2.2: Chuẩn bị sample documents (15 phút)

**Tạo file `docs/company_policy.md`:**
```markdown
# Company Policies

## Leave Policy
- Annual leave: 12 days per year for all full-time employees
- Sick leave: 30 days per year with medical certificate
- Maternity leave: 6 months as per Vietnamese labor law
- Paternity leave: 5 working days
- Leave requests must be submitted at least 3 days in advance via HR Portal

## Remote Work Policy
- Employees may work remotely up to 2 days per week
- Remote work requires manager approval
- Core hours: 10:00 AM - 4:00 PM (must be available online)
- VPN connection required when accessing company systems remotely

## Code Review Policy
- All code changes require at least 1 reviewer approval
- Reviews should be completed within 24 hours
- Use conventional commits format
- All CI checks must pass before merge

## Security Policy
- Two-factor authentication (2FA) required for all company accounts
- Passwords must be at least 12 characters
- Do not store credentials in source code
- Report security incidents to security@company.com within 24 hours

## Onboarding Process
- New employees receive company laptop on day 1
- IT setup appointment scheduled within first 2 hours
- Buddy system: each new hire paired with experienced team member
- First week: complete mandatory training modules on LMS
- 30-60-90 day check-ins with manager
```

> **Tại sao dùng sample doc tiếng Anh?** Dễ test, embedding model hoạt động tốt hơn.
> Sau khi flow chạy rồi, thay bằng doc tiếng Việt bất cứ lúc nào.

### Bước 2.3: Config module (15 phút)

**File `src/agent/config.py`:**
```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    google_api_key: str
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "knowledge_base"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 3

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
```

> **Giải thích pydantic-settings:**
> - Tự đọc `.env` file và map vào class attributes
> - `extra = "ignore"`: bỏ qua env vars không khai báo (tránh lỗi)
> - Type validation tự động: nếu `chunk_size` nhận string → lỗi rõ ràng
> - Đây là pattern chuẩn production: KHÔNG BAO GIỜ hardcode secrets

### Bước 2.4: Ingestion pipeline (60 phút)

**File `src/rag/__init__.py`:**
```python
```

**File `src/rag/ingest.py`:**
```python
"""Document ingestion: load files → chunk text → embed → store in Qdrant."""

import hashlib
from pathlib import Path

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from src.agent.config import settings


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks.

    Args:
        text: The input text to split.
        chunk_size: Maximum characters per chunk.
        overlap: Number of overlapping characters between consecutive chunks.

    Returns:
        List of text chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c.strip() for c in chunks if c.strip()]


def load_documents(docs_dir: str = "docs") -> list[dict]:
    """Load all .md and .txt files, chunk them, return list of dicts."""
    docs = []
    for path in Path(docs_dir).glob("**/*"):
        if path.suffix in (".md", ".txt"):
            content = path.read_text(encoding="utf-8")
            chunks = chunk_text(
                content,
                chunk_size=settings.chunk_size,
                overlap=settings.chunk_overlap,
            )
            for i, chunk in enumerate(chunks):
                docs.append(
                    {
                        "id": hashlib.md5(f"{path.name}_{i}".encode()).hexdigest(),
                        "text": chunk,
                        "metadata": {
                            "source": path.name,
                            "chunk_index": i,
                        },
                    }
                )
    return docs


def ingest(docs_dir: str = "docs") -> int:
    """Full ingestion pipeline: load docs → embed → upsert to Qdrant.

    Returns:
        Number of chunks ingested.
    """
    client = QdrantClient(url=settings.qdrant_url)
    embed_model = TextEmbedding(model_name=settings.embedding_model)

    # Load & chunk documents
    documents = load_documents(docs_dir)
    if not documents:
        print("No documents found.")
        return 0

    texts = [doc["text"] for doc in documents]

    # Generate embeddings
    embeddings = list(embed_model.embed(texts))
    vector_size = len(embeddings[0])

    # Create collection (recreate if exists for clean ingestion)
    client.recreate_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    # Build and upsert points
    points = [
        PointStruct(
            id=idx,
            vector=embeddings[idx].tolist(),
            payload={"text": documents[idx]["text"], **documents[idx]["metadata"]},
        )
        for idx in range(len(documents))
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=points)

    print(f"Ingested {len(points)} chunks into '{settings.qdrant_collection}'")
    return len(points)


if __name__ == "__main__":
    ingest()
```

**File `scripts/ingest_docs.py`:**
```python
"""CLI script to ingest documents into Qdrant.

Usage: uv run python -m scripts.ingest_docs
"""

from src.rag.ingest import ingest

if __name__ == "__main__":
    count = ingest()
    print(f"Done. Total chunks: {count}")
```

> **Flow giải thích:**
> 1. `load_documents()`: đọc tất cả .md/.txt trong `docs/` → chunk thành đoạn nhỏ
> 2. `fastembed` chạy embedding model LOCAL (không cần API) → ra vectors
> 3. Tạo Qdrant collection → upsert vectors + metadata
> 4. Mỗi chunk lưu kèm source file name để citation

### Bước 2.5: Retriever (30 phút)

**File `src/rag/retriever.py`:**
```python
"""Retrieve relevant chunks from Qdrant vector database."""

from fastembed import TextEmbedding
from qdrant_client import QdrantClient

from src.agent.config import settings

# Initialize once at module level (singleton pattern - tránh khởi tạo lại mỗi request)
_client = QdrantClient(url=settings.qdrant_url)
_embed_model = TextEmbedding(model_name=settings.embedding_model)


def search_knowledge(query: str, top_k: int | None = None) -> list[dict]:
    """Search Qdrant for chunks most relevant to the query.

    Args:
        query: Natural language search query.
        top_k: Number of results to return. Defaults to settings.top_k.

    Returns:
        List of dicts with keys: text, source, score.
    """
    top_k = top_k or settings.top_k

    # Embed the query using same model as ingestion
    query_embedding = list(_embed_model.embed([query]))[0].tolist()

    # Search Qdrant
    results = _client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_embedding,
        limit=top_k,
    ).points

    return [
        {
            "text": point.payload["text"],
            "source": point.payload.get("source", "unknown"),
            "score": point.score,
        }
        for point in results
    ]
```

### Bước 2.6: Kết nối RAG vào Agent làm tool (30 phút)

**File `src/agent/tools.py`:**
```python
"""Custom tools for the knowledge assistant agent."""

from src.rag.retriever import search_knowledge


def search_company_knowledge(query: str) -> dict:
    """Search the company knowledge base for relevant information.

    Use this tool when the user asks about company policies, procedures,
    or any internal knowledge. Always search before answering policy questions.

    Args:
        query: The search query describing what information to find.

    Returns:
        A dictionary with search results containing relevant text chunks and sources.
    """
    results = search_knowledge(query)

    if not results:
        return {"status": "no_results", "message": "No relevant information found."}

    formatted = []
    for r in results:
        formatted.append(f"[Source: {r['source']}] {r['text']}")

    return {
        "status": "success",
        "results": formatted,
        "num_results": len(results),
    }
```

> **Quan trọng:** Docstring của tool = instruction cho LLM.
> ADK đọc docstring để biết KHI NÀO gọi tool và CÁCH sử dụng.
> Viết docstring rõ ràng = agent gọi tool chính xác hơn.

**Update `src/agent/agent.py`:**
```python
from google.adk import Agent

from .tools import search_company_knowledge

agent = Agent(
    model="gemini-2.0-flash",
    name="knowledge_assistant",
    description="Enterprise knowledge assistant that helps employees find information.",
    instruction="""You are a helpful enterprise knowledge assistant.

    Your role:
    - Answer questions about company policies, procedures, and knowledge base
    - ALWAYS use the search_company_knowledge tool before answering policy questions
    - Be concise and accurate
    - Cite the source document when using retrieved information
    - If the search returns no results, say you don't have that information
    """,
    tools=[search_company_knowledge],
)
```

### Bước 2.7: Test toàn bộ flow (15 phút)

```bash
# 1. Đảm bảo Qdrant đang chạy
docker compose up qdrant -d

# 2. Ingest documents (lần đầu sẽ download embedding model ~50MB)
uv run python -m scripts.ingest_docs
# Expected: "Ingested X chunks into 'knowledge_base'"

# 3. Chạy agent
uv run adk web src

# 4. Mở browser → hỏi các câu:
#    - "What is the remote work policy?"
#    - "How many annual leave days do I get?"
#    - "What is the onboarding process?"
#    → Agent PHẢI gọi search_company_knowledge → trả lời với citation [Source: ...]
```

```bash
git add .
git commit -m "feat: add RAG pipeline (Qdrant + fastembed) + connect to ADK agent"
git push
```

### ✅ Checkpoint Day 2:
- [ ] Qdrant chạy trong Docker, dashboard accessible
- [ ] `scripts/ingest_docs.py` chạy smooth, in ra số chunks
- [ ] Hỏi agent câu hỏi policy → agent gọi search tool → trả lời đúng với source citation
- [ ] Hiểu: Docker compose là gì, embedding là gì, vector search hoạt động thế nào

---

## Day 3 (3-4h): FastAPI Serving + Clean Code

### Mục tiêu: Agent serve qua HTTP API, code structure clean & typed

---

### Bước 3.1: Thêm ruff config vào pyproject.toml (10 phút)

**Thêm vào `pyproject.toml`:**
```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B"]
# E = pycodestyle errors
# F = pyflakes
# I = isort (import ordering)
# N = pep8 naming
# UP = pyupgrade (modern Python syntax)
# B = flake8-bugbear (common bugs)

[tool.ruff.format]
quote-style = "double"
```

### Bước 3.2: FastAPI app với ADK built-in (45 phút)

**File `src/app.py`:**
```python
"""FastAPI application serving the ADK agent."""

import uvicorn
from dotenv import load_dotenv

# Load .env BEFORE importing anything that uses settings
load_dotenv()

from google.adk.cli.fast_api import get_fast_api_app  # noqa: E402

# ADK's helper creates a FastAPI app with built-in endpoints:
# - Web UI at /
# - SSE streaming at /run_sse
# - Session management
app = get_fast_api_app(
    agents_dir="src",
    web=True,
)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for Docker/load balancer probes."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
```

**Test:**
```bash
uv run python -m src.app
# Mở http://localhost:8000 → ADK web UI (giống adk web)
# Test health: curl http://localhost:8000/health
```

### Bước 3.3: Custom REST chat endpoint (45 phút)

> **Tại sao cần custom endpoint?**
> ADK built-in dùng SSE (Server-Sent Events) — phức tạp cho client.
> Custom REST endpoint đơn giản hơn: POST JSON → nhận JSON.

**Thêm vào `src/app.py` (sau phần `app = get_fast_api_app(...)`):**
```python
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from src.agent import agent


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    message: str
    session_id: str = "default"
    user_id: str = "user"


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""
    response: str
    session_id: str


# Session service lưu conversation history trong memory
# Production: dùng DatabaseSessionService thay InMemorySessionService
session_service = InMemorySessionService()
runner = Runner(
    agent=agent,
    app_name="knowledge_assistant",
    session_service=session_service,
)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Simple REST endpoint for chat. Send message, get response."""
    # Get or create session (session = conversation thread)
    session = await session_service.get_session(
        app_name="knowledge_assistant",
        user_id=request.user_id,
        session_id=request.session_id,
    )
    if session is None:
        session = await session_service.create_session(
            app_name="knowledge_assistant",
            user_id=request.user_id,
            session_id=request.session_id,
        )

    # Create user message in ADK format
    user_message = Content(role="user", parts=[Part(text=request.message)])

    # Run agent and collect final response
    final_response = ""
    async for event in runner.run_async(
        user_id=request.user_id,
        session_id=request.session_id,
        new_message=user_message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text

    return ChatResponse(response=final_response, session_id=request.session_id)
```

**Test REST endpoint:**
```bash
# Terminal 1: chạy app
uv run python -m src.app

# Terminal 2: test với curl
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How many annual leave days do I get?"}'

# Expected response:
# {"response":"Based on the company policy, full-time employees receive 12 annual leave days per year. [Source: company_policy.md]","session_id":"default"}

# Test session continuity (cùng session_id → agent nhớ context):
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "And what about sick leave?", "session_id": "test1"}'
```

### Bước 3.4: Clean code pass (20 phút)

```bash
# Format tất cả code
uv run ruff format .

# Lint + auto-fix những gì fix được
uv run ruff check . --fix

# Check lại (phải clean)
uv run ruff check .
```

**Checklist clean code (đọc qua từng file):**
- [ ] Tất cả functions có type hints (params + return type)
- [ ] Public functions có docstring (ít nhất 1 dòng)
- [ ] Không hardcode API keys hay URLs (tất cả qua `settings`)
- [ ] Import order: stdlib → third-party → local (ruff tự fix)
- [ ] Không có commented-out code
- [ ] Không có `print()` debug còn sót (trừ scripts)

```bash
git add .
git commit -m "feat: add FastAPI serving with custom chat endpoint + clean code"
git push
```

### ✅ Checkpoint Day 3:
- [ ] `GET /health` → `{"status": "ok"}`
- [ ] `POST /api/chat` → trả response đúng
- [ ] `ruff check .` → no errors
- [ ] `ruff format --check .` → no changes needed
- [ ] Hiểu: FastAPI request/response model, async/await, ADK Runner pattern

---

## Day 4 (3-4h): Testing - pytest + ADK Eval

### Mục tiêu: Test suite chạy green, hiểu cách viết test chuẩn

---

### Bước 4.1: pytest config (10 phút)

**Thêm vào `pyproject.toml`:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
filterwarnings = ["ignore::DeprecationWarning"]
```

> **Giải thích:**
> - `testpaths`: pytest chỉ scan folder `tests/`
> - `asyncio_mode = "auto"`: tự detect async test functions (không cần `@pytest.mark.asyncio` mỗi test)

### Bước 4.2: Shared fixtures (20 phút)

**File `tests/conftest.py`:**
```python
"""Shared test fixtures.

Fixtures = dữ liệu/objects dùng chung giữa các test files.
pytest tự inject fixture vào test function qua parameter name.
"""

import pytest


@pytest.fixture
def sample_chunks() -> list[dict]:
    """Sample search results for testing tools."""
    return [
        {
            "text": "Annual leave: 12 days per year for full-time employees.",
            "source": "company_policy.md",
            "score": 0.95,
        },
        {
            "text": "Remote work requires manager approval. Core hours: 10AM-4PM.",
            "source": "company_policy.md",
            "score": 0.87,
        },
    ]


@pytest.fixture
def sample_documents() -> list[str]:
    """Sample raw documents for ingestion testing."""
    return [
        "Annual leave is 12 days per year. Sick leave is 30 days with certificate.",
        "Remote work is allowed 2 days per week with manager approval.",
        "All code changes require at least 1 reviewer approval before merge.",
    ]
```

### Bước 4.3: Unit test - Chunking logic (20 phút)

**File `tests/test_ingest.py`:**
```python
"""Tests for document ingestion pipeline.

Test chunking logic riêng vì nó là pure function (không cần mock DB).
"""

from src.rag.ingest import chunk_text


class TestChunkText:
    """Test the text chunking function."""

    def test_basic_chunking(self):
        """Long text should be split into multiple chunks."""
        text = "a" * 1000
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        assert len(chunks) >= 2
        assert all(len(c) <= 500 for c in chunks)

    def test_overlap_exists(self):
        """Consecutive chunks should share overlapping content."""
        text = "word " * 200  # 1000 chars
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        assert len(chunks) >= 2
        # Last 20 chars of chunk[0] should appear in chunk[1]

    def test_empty_text_returns_empty(self):
        """Empty input should return empty list, not error."""
        chunks = chunk_text("")
        assert chunks == []

    def test_short_text_single_chunk(self):
        """Text shorter than chunk_size should return 1 chunk."""
        chunks = chunk_text("Hello world", chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0] == "Hello world"

    def test_custom_parameters(self):
        """Custom chunk_size and overlap should be respected."""
        text = "x" * 300
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) >= 3
```

### Bước 4.4: Unit test - Agent tools with mocking (30 phút)

**File `tests/test_tools.py`:**
```python
"""Tests for agent tools.

Mock external dependencies (Qdrant) để test logic riêng.
Tại sao mock? Vì unit test KHÔNG nên phụ thuộc vào database đang chạy.
"""

from unittest.mock import patch

from src.agent.tools import search_company_knowledge


class TestSearchCompanyKnowledge:
    """Test the search tool that agent calls."""

    @patch("src.agent.tools.search_knowledge")
    def test_returns_formatted_results(self, mock_search, sample_chunks):
        """When Qdrant returns results, tool should format them properly."""
        mock_search.return_value = sample_chunks

        result = search_company_knowledge("leave policy")

        assert result["status"] == "success"
        assert result["num_results"] == 2
        assert len(result["results"]) == 2
        # Verify source citation is included
        assert "[Source: company_policy.md]" in result["results"][0]
        mock_search.assert_called_once_with("leave policy")

    @patch("src.agent.tools.search_knowledge")
    def test_handles_no_results(self, mock_search):
        """When Qdrant returns nothing, tool should return no_results status."""
        mock_search.return_value = []

        result = search_company_knowledge("completely random query xyz")

        assert result["status"] == "no_results"
        assert "message" in result
```

> **Giải thích @patch:**
> `@patch("src.agent.tools.search_knowledge")` = thay function thật bằng mock
> → test chỉ kiểm tra logic formatting, KHÔNG gọi Qdrant thật
> → test chạy nhanh, không cần Docker

### Bước 4.5: API endpoint test (30 phút)

**File `tests/test_app.py`:**
```python
"""Tests for FastAPI endpoints.

Dùng httpx AsyncClient để test endpoints mà không cần start server thật.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.app import app


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoint:
    """Test health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client):
        """Health endpoint should return 200 with status ok."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
```

### Bước 4.6: Chạy tests (15 phút)

```bash
# Chạy tất cả tests với output chi tiết
uv run pytest -v

# Expected output:
# tests/test_ingest.py::TestChunkText::test_basic_chunking PASSED
# tests/test_ingest.py::TestChunkText::test_overlap_exists PASSED
# tests/test_ingest.py::TestChunkText::test_empty_text_returns_empty PASSED
# tests/test_ingest.py::TestChunkText::test_short_text_single_chunk PASSED
# tests/test_ingest.py::TestChunkText::test_custom_parameters PASSED
# tests/test_tools.py::TestSearchCompanyKnowledge::test_returns_formatted_results PASSED
# tests/test_tools.py::TestSearchCompanyKnowledge::test_handles_no_results PASSED
# tests/test_app.py::TestHealthEndpoint::test_health_returns_ok PASSED

# Chạy với coverage (optional):
# uv add --dev pytest-cov
# uv run pytest --cov=src -v
```

### Bước 4.7: ADK Eval (nếu dư thời gian, 30 phút)

**File `tests/evals/knowledge_qa.test.json`:**
```json
[
  {
    "name": "leave_policy_question",
    "input": "How many annual leave days do employees get?",
    "expected_tool_use": ["search_company_knowledge"],
    "reference_answer": "12 days"
  },
  {
    "name": "remote_work_question",
    "input": "Can I work from home?",
    "expected_tool_use": ["search_company_knowledge"],
    "reference_answer": "2 days per week"
  },
  {
    "name": "security_question",
    "input": "What are the password requirements?",
    "expected_tool_use": ["search_company_knowledge"],
    "reference_answer": "at least 12 characters"
  }
]
```

```bash
# Cần Qdrant chạy + documents ingested
uv run adk eval src/agent tests/evals/knowledge_qa.test.json
```

```bash
git add .
git commit -m "feat: add pytest test suite (unit + API + fixtures)"
git push
```

### ✅ Checkpoint Day 4:
- [ ] `uv run pytest -v` → ALL PASSED
- [ ] `uv run ruff check .` → clean
- [ ] Hiểu: fixture là gì, mock/patch dùng khi nào, async test pattern
- [ ] Hiểu: tại sao mock external deps, tại sao không test trực tiếp Qdrant

---

## Day 5 (3-4h): Docker Production Packaging

### Mục tiêu: `docker compose up` → toàn bộ system chạy trong containers

---

### Bước 5.1: Dockerfile multi-stage build (45 phút)

**File `Dockerfile`:**
```dockerfile
# ==========================
# Stage 1: Builder
# ==========================
FROM python:3.11-slim AS builder

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files FIRST (Docker cache optimization)
# Nếu chỉ thay đổi code mà không đổi deps → layer này được cache → build nhanh hơn
COPY pyproject.toml uv.lock* ./

# Install dependencies (không install project code vì chưa copy)
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code
COPY src/ src/
COPY scripts/ scripts/
COPY docs/ docs/

# Install the project itself
RUN uv sync --frozen --no-dev

# ==========================
# Stage 2: Runtime (lighter)
# ==========================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy ONLY the virtual environment from builder (không copy build tools)
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app/src ./src
COPY --from=builder /app/scripts ./scripts
COPY --from=builder /app/docs ./docs

# Use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Health check: Docker tự check app còn sống không
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start the application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

> **Multi-stage build giải thích:**
> - **Stage 1 (builder):** Cài tất cả dependencies, build tools, compile nếu cần
> - **Stage 2 (runtime):** Chỉ copy kết quả cuối cùng (.venv + code)
> - **Kết quả:** Image nhỏ hơn đáng kể (không chứa uv, build tools, cache)
> - **Cache layer:** `pyproject.toml` copy TRƯỚC code → nếu chỉ đổi code, Docker skip bước install deps

### Bước 5.2: .dockerignore (5 phút)

**File `.dockerignore`:**
```
.git
.github
.env
.venv
__pycache__
*.pyc
.pytest_cache
.ruff_cache
tests/
*.md
!docs/*.md
```

### Bước 5.3: docker-compose.yml đầy đủ (20 phút)

**Update `docker-compose.yml`:**
```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      qdrant:
        condition: service_healthy  # Chờ Qdrant ready mới start app
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:6333/readyz"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  qdrant_data:
```

> **Giải thích docker-compose:**
> - `depends_on: condition: service_healthy`: app chờ Qdrant healthcheck pass
> - `env_file: .env`: load env vars từ .env file vào container
> - `restart: unless-stopped`: auto restart nếu app crash
> - `volumes: qdrant_data`: data persist qua restart (không mất khi `docker compose down`)

### Bước 5.4: Test toàn bộ Docker flow (45 phút)

```bash
# 1. Build và chạy tất cả services
docker compose up --build -d

# 2. Check status (chờ cả 2 "healthy")
docker compose ps
# NAME          SERVICE   STATUS
# app           app       Up (healthy)
# qdrant        qdrant    Up (healthy)

# 3. Ingest documents
# Lưu ý: chạy từ HOST machine, Qdrant accessible qua localhost:6333
uv run python -m scripts.ingest_docs

# 4. Test endpoints
curl http://localhost:8000/health
# {"status":"ok"}

curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the code review policy?"}'

# 5. Xem logs nếu có lỗi
docker compose logs app
docker compose logs qdrant

# 6. Check image size
docker images | grep prod-agent-adk
# Nên < 500MB

# 7. Cleanup
docker compose down
# Muốn xóa cả data: docker compose down -v
```

**Troubleshooting thường gặp:**
```bash
# App không connect được Qdrant?
# → Check .env: QDRANT_URL phải là http://qdrant:6333 (tên service, không phải localhost)
#    vì trong Docker network, services gọi nhau bằng service name

# Cách fix: trong .env thêm dòng cho Docker:
# QDRANT_URL=http://qdrant:6333  (khi chạy docker compose)
# QDRANT_URL=http://localhost:6333  (khi chạy local dev)
```

```bash
git add .
git commit -m "feat: add Dockerfile multi-stage + docker-compose full system"
git push
```

### ✅ Checkpoint Day 5:
- [ ] `docker compose up --build` → cả app + qdrant khởi động
- [ ] `curl /health` → OK
- [ ] `curl /api/chat` → response đúng
- [ ] `docker images` → image < 500MB
- [ ] Hiểu: Dockerfile layers, multi-stage build, docker-compose networking

---

## Day 6 (3-4h): CI/CD - GitHub Actions + Cloud Run

### Mục tiêu: Push code → tự động test → tự động build Docker

---

### Bước 6.1: GitHub Actions CI workflow (60 phút)

**File `.github/workflows/ci.yml`:**
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Env vars cho test (fake values, không cần real API key)
env:
  GOOGLE_API_KEY: "fake-key-for-ci"
  QDRANT_URL: "http://localhost:6333"

jobs:
  # Job 1: Lint code
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Install dependencies
        run: uv sync --dev

      - name: Lint with ruff
        run: uv run ruff check .

      - name: Check formatting
        run: uv run ruff format --check .

  # Job 2: Run tests (chỉ chạy sau lint pass)
  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Install dependencies
        run: uv sync --dev

      - name: Run tests
        run: uv run pytest -v

  # Job 3: Build Docker image (chỉ chạy sau test pass)
  docker-build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t prod-agent-adk:${{ github.sha }} .

      - name: Verify image was created
        run: docker images prod-agent-adk
```

> **Giải thích GitHub Actions:**
> - `on: push/pull_request`: trigger khi push hoặc tạo PR vào main
> - `needs: lint/test`: dependency chain: lint → test → docker-build
> - `${{ github.sha }}`: tag image bằng commit hash (traceability)
> - `env: GOOGLE_API_KEY: "fake"`: test không cần real key (mock Qdrant)

### Bước 6.2: Test CI locally trước khi push (15 phút)

```bash
# Giả lập CI steps trên máy mình
uv run ruff check .          # lint
uv run ruff format --check . # format check
uv run pytest -v             # tests
docker build -t prod-agent-adk:test .  # docker build

# Nếu tất cả pass → push lên GitHub
git add .
git commit -m "feat: add GitHub Actions CI pipeline (lint + test + docker build)"
git push
```

**Kiểm tra CI trên GitHub:**
```
1. Mở https://github.com/YOUR_USERNAME/prod-agent-adk/actions
2. Xem workflow "CI" chạy
3. Cả 3 jobs phải green: lint ✅ → test ✅ → docker-build ✅
```

### Bước 6.3: Cloud Run deploy documentation (45 phút)

> **Lưu ý:** Phần này anh có thể chỉ document flow mà KHÔNG deploy thật (tiết kiệm tiền).
> Cloud Run free tier: 2M requests/month, 360K GB-seconds compute.
> Nhưng cần billing account (có thể bị charge nếu vượt).

**Option A: Manual deploy (đơn giản nhất)**

Tạo file `docs/DEPLOY.md`:
```markdown
# Deploy to Google Cloud Run

## Prerequisites
1. Google Cloud account with billing enabled
2. gcloud CLI installed: https://cloud.google.com/sdk/docs/install
3. Qdrant Cloud cluster (free tier): https://cloud.qdrant.io/

## Steps

### 1. Setup Qdrant Cloud
- Go to https://cloud.qdrant.io/ → Create free cluster
- Note the URL (e.g., https://xxx.us-east4-0.gcp.cloud.qdrant.io)
- Create API key
- Run ingestion pointing to cloud Qdrant:
  QDRANT_URL=https://xxx.cloud.qdrant.io QDRANT_API_KEY=your-key uv run python -m scripts.ingest_docs

### 2. Deploy to Cloud Run
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Deploy directly from source (Cloud Build builds the Docker image)
gcloud run deploy prod-agent-adk \
  --source . \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_API_KEY=your-gemini-key" \
  --set-env-vars "QDRANT_URL=your-qdrant-cloud-url"
```

### 3. Verify
```bash
# Get the service URL
gcloud run services describe prod-agent-adk --region asia-southeast1 --format="value(status.url)"

# Test
curl https://YOUR_SERVICE_URL/health
curl -X POST https://YOUR_SERVICE_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the leave policy?"}'
```
```

**Option B: Auto deploy via CI (thêm vào ci.yml nếu muốn)**

```yaml
  # Thêm job này vào .github/workflows/ci.yml
  deploy:
    runs-on: ubuntu-latest
    needs: docker-build
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy prod-agent-adk \
            --source . \
            --region asia-southeast1 \
            --allow-unauthenticated \
            --set-env-vars "GOOGLE_API_KEY=${{ secrets.GOOGLE_API_KEY }}" \
            --set-env-vars "QDRANT_URL=${{ secrets.QDRANT_URL }}"
```

```bash
git add .
git commit -m "feat: add Cloud Run deploy documentation"
git push
```

### ✅ Checkpoint Day 6:
- [ ] Push commit → GitHub Actions chạy green (lint ✅ test ✅ docker build ✅)
- [ ] Hiểu CI/CD flow: push → lint → test → build → (deploy)
- [ ] Có deploy documentation/config sẵn sàng
- [ ] Hiểu: GitHub Actions syntax (jobs, steps, needs, env, secrets)

---

## Day 7 (3-4h): Polish + Review + Demo Preparation

### Mục tiêu: Project demo-ready, tự tin onboard

---

### Bước 7.1: Viết README.md (45 phút)

**File `README.md`:**
```markdown
# Production RAG Agent (Google ADK)

Enterprise knowledge assistant powered by Google Agent Development Kit + Qdrant.

## Architecture

```
User Request
    ↓
FastAPI (/api/chat)
    ↓
ADK Runner
    ↓
Knowledge Assistant Agent (Gemini 2.0 Flash)
    ↓ (tool call)
search_company_knowledge()
    ↓
Qdrant Vector Search
    ↓
Retrieved chunks + source citations
    ↓
Agent generates final response
    ↓
JSON Response to User
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | Google ADK |
| LLM | Gemini 2.0 Flash |
| Vector DB | Qdrant |
| Embeddings | FastEmbed (BAAI/bge-small-en-v1.5) |
| API | FastAPI |
| Package Manager | uv |
| Linting | Ruff |
| Testing | pytest |
| CI/CD | GitHub Actions → Docker → Cloud Run |

## Quick Start (Local Development)

```bash
# 1. Clone & install
git clone https://github.com/YOUR_USERNAME/prod-agent-adk.git
cd prod-agent-adk
cp .env.example .env  # ← fill in your GOOGLE_API_KEY
uv sync

# 2. Start Qdrant & ingest sample documents
docker compose up qdrant -d
uv run python -m scripts.ingest_docs

# 3. Run the app
uv run python -m src.app
# → Open http://localhost:8000
```

## Docker (Full Stack)

```bash
docker compose up --build
# App: http://localhost:8000
# Qdrant: http://localhost:6333/dashboard
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/chat` | Chat with agent |
| GET | `/` | ADK Web UI |

### Example: Chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the remote work policy?", "session_id": "user1"}'
```

## Testing

```bash
uv run pytest -v          # Run tests
uv run ruff check .       # Lint
uv run ruff format .      # Format
```

## Deployment

See [docs/DEPLOY.md](docs/DEPLOY.md) for Cloud Run deployment guide.
```

### Bước 7.2: Review toàn bộ code (60 phút)

**Chạy checklist này từng bước:**

```bash
# 1. Code quality
uv run ruff check .
uv run ruff format --check .

# 2. Tests pass
uv run pytest -v

# 3. No secrets committed
git log --all -p --diff-filter=A -- "*.env" | head -20
# Phải không có output (không có .env nào bị commit)

# 4. Imports work
uv run python -c "from src.agent import agent; print(f'Agent: {agent.name}')"
uv run python -c "from src.rag.ingest import chunk_text; print(chunk_text('test', 10))"

# 5. Docker builds
docker build -t prod-agent-adk:final .
docker images prod-agent-adk

# 6. Docker compose runs
docker compose up --build -d
docker compose ps
curl http://localhost:8000/health
docker compose down
```

### Bước 7.3: Fresh clone test (30 phút)

```bash
# Simulate someone cloning repo lần đầu
cd /tmp
git clone https://github.com/YOUR_USERNAME/prod-agent-adk.git fresh-test
cd fresh-test

# Follow README exactly
cp .env.example .env
# Điền GOOGLE_API_KEY

uv sync
docker compose up qdrant -d
uv run python -m scripts.ingest_docs
uv run pytest -v
uv run python -m src.app

# Test: mở browser, chat, verify hoạt động
# Nếu có step nào fail → fix README + code → commit
```

### Bước 7.4: Chuẩn bị talking points cho ngày đầu (15 phút)

**Khi được hỏi "em đã làm gì trước khi vào?":**

1. **Project overview:** "Em đã build một enterprise knowledge assistant dùng Google ADK + Qdrant, có API, Docker, CI/CD pipeline đầy đủ."

2. **Why Google ADK:** "Native tool-calling, built-in eval framework cho agent quality, dễ scale lên multi-agent. Google đang push mạnh framework này."

3. **Why Qdrant:** "Native integration với ADK, popular trong enterprise projects, free tier tốt, API đơn giản."

4. **Architecture decisions:**
   - "Config qua env vars (12-factor app)"
   - "Multi-stage Docker build (image nhỏ, build nhanh)"
   - "Tách agent logic / RAG logic / serving logic (separation of concerns)"
   - "Mock external deps trong tests (unit test nhanh, không cần DB)"

5. **Nếu được hỏi "next steps":**
   - "Thêm authentication, multi-agent orchestration, monitoring"
   - "Switch sang DatabaseSessionService cho production"
   - "Thêm document versioning trong ingestion pipeline"

```bash
git add .
git commit -m "docs: add README + final polish"
git push
```

### ✅ Checkpoint Day 7 (FINAL):
- [ ] README rõ ràng, ai clone cũng follow được
- [ ] Fresh clone → chạy được trong 5 phút
- [ ] CI pipeline green trên GitHub
- [ ] Có thể explain architecture trong 2 phút
- [ ] Tự tin: biết project structure, biết test, biết Docker, biết CI/CD

---

## Tổng kết

### SKIP được (không làm tuần này):
- ❌ Kubernetes (quá sớm, Cloud Run đủ cho MVP)
- ❌ Frontend UI (API-first, dùng ADK web UI hoặc curl)
- ❌ Authentication/authorization (để khi có yêu cầu cụ thể)
- ❌ Monitoring/observability (Arize, Langfuse — để sau)
- ❌ Complex multi-agent orchestration (làm 1 agent solid trước)
- ❌ Multiple vector DB support (chỉ Qdrant)

### BẮT BUỘC biết trước ngày đầu:
- ✅ Git workflow: branch, commit, push, PR
- ✅ Python project structure: src layout, pyproject.toml, __init__.py
- ✅ Docker basics: Dockerfile, docker compose, multi-stage build
- ✅ Testing: pytest fixtures, mocking, async tests
- ✅ CI/CD: GitHub Actions pipeline
- ✅ ADK: Agent anatomy, custom tools, Runner pattern

### Daily Summary:
| Day | Theme | Key Output |
|-----|-------|------------|
| 1 | Project Setup + ADK | Agent chạy, repo trên GitHub |
| 2 | RAG Pipeline | Agent search Qdrant, trả lời có citation |
| 3 | FastAPI + Clean Code | HTTP API hoạt động, code linted |
| 4 | Testing | pytest suite green, hiểu mocking |
| 5 | Docker | `docker compose up` chạy full system |
| 6 | CI/CD | GitHub Actions green, deploy config sẵn |
| 7 | Polish + Demo | README clear, fresh clone works, confident |

---

## Resources

| Chủ đề | Link |
|--------|------|
| ADK Docs | https://adk.dev/ |
| ADK Samples | https://github.com/google/adk-samples |
| ADK Python Source | https://github.com/google/adk-python |
| Qdrant + ADK Integration | https://google.github.io/adk-docs/integrations/qdrant/ |
| FastAPI + ADK Guide | https://medium.com/google-cloud/get-schwifty-with-the-fastapi |
| pytest Documentation | https://docs.pytest.org/ |
| Ruff Linter | https://docs.astral.sh/ruff/ |
| uv Package Manager | https://docs.astral.sh/uv/ |
| Qdrant Cloud (free) | https://cloud.qdrant.io/ |
| Cloud Run | https://cloud.google.com/run |
| Gemini API Key | https://aistudio.google.com/apikey |
