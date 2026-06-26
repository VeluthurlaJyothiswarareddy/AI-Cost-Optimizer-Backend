# AI Cost Optimizer — Backend

FastAPI backend for the AI Cost Optimization POC. Three independent optimization modules share OpenRouter and MongoDB but use separate routers, services, and collections.

See the [root README](../README.md) for full documentation, examples, and architecture.

## Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- [OpenRouter](https://openrouter.ai/) API key

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OPENROUTER_API_KEY
```

## Run

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `OPENROUTER_BASE_URL` | Default: `https://openrouter.ai/api/v1` |
| `MONGO_URI` | Default: `mongodb://localhost:27017` |
| `DATABASE_NAME` | Default: `ai_cost_optimizer` |

## API Endpoints

### Max Token Optimization

| Method | Path |
|--------|------|
| `POST` | `/api/chat` |
| `GET` | `/api/history` |
| `GET` | `/api/metrics` |

### Prompt Prefix Caching

| Method | Path |
|--------|------|
| `POST` | `/api/prefix-cache/chat` |
| `GET` | `/api/prefix-cache/metrics` |

### Model Tiering

| Method | Path |
|--------|------|
| `POST` | `/api/model-tiering/chat` |
| `GET` | `/api/model-tiering/history` |
| `GET` | `/api/model-tiering/metrics` |

### Health

| Method | Path |
|--------|------|
| `GET` | `/health` |

## MongoDB Collections

| Collection | Module |
|------------|--------|
| `llm_requests` | Max Token Optimization |
| `prompt_cache` | Prompt Prefix Caching |
| `model_routing_requests` | Model Tiering |

## Quick Test

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain Redis","model":"openai/gpt-4o-mini","max_tokens":100}'
```
