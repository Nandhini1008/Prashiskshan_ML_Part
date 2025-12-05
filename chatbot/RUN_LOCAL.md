# Running Chatbot Service Locally

## Overview

The chatbot service runs **locally** (outside Docker) and connects to Redis and Qdrant running in Docker containers.

## Prerequisites

1. **Docker services running:**
   ```bash
   cd Prashiskshan_backend
   docker-compose up -d redis qdrant
   ```

2. **Python environment:**
   ```bash
   # From project root
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r Prashiskshan_ml/chatbot/requirements.txt
   ```

3. **Environment variables:**
   Make sure `.env` file exists in `Prashiskshan_ml/chatbot/` with:
   ```bash
   REDIS_HOST=localhost
   REDIS_PORT=6379
   QDRANT_URL=http://localhost:6333
   GEMINI_API_KEY=your_api_key_here
   ```

## Running the Service

### Start the chatbot service:

```bash
cd Prashiskshan_ml/chatbot
python chatbot_service_sse.py
```

You should see:
```
Initializing chatbot service...
RAG Chatbot initialized successfully!
🔥 Pre-warming RAG pipeline...
  → Loading sentence transformer into memory...
  ✓ Sentence transformer loaded
  → Warming up Qdrant connection...
  ✓ Qdrant connection warmed
✅ Pipeline pre-warmed in X.XXs
Starting SSE-enabled chatbot service on 0.0.0.0:5001
```

### Test the service:

```bash
# Health check
curl http://localhost:5001/health

# Expected response:
{
  "status": "ok",
  "chatbot_initialized": true,
  "pipeline_warmed": true,
  "redis_connected": true
}
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Docker Containers                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Redis   │  │  Qdrant  │  │  MongoDB │     │
│  │  :6379   │  │  :6333   │  │  :27017  │     │
│  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────┘
         ▲              ▲
         │              │
         │              │
┌────────┴──────────────┴─────────────────────────┐
│  Local Python Process                           │
│  ┌───────────────────────────────────────────┐  │
│  │  Chatbot Service (chatbot_service_sse.py) │  │
│  │  - LangGraph Pipeline                     │  │
│  │  - RAG with Qdrant                        │  │
│  │  - Conversation Memory (Redis)            │  │
│  │  - SSE Streaming                          │  │
│  │  Port: 5001                               │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Conversation Storage

Conversations are stored in Redis with LangGraph:

- **Key Pattern:** `chatbot:{user_id}:{session_id}`
- **Storage:** Redis (running in Docker)
- **TTL:** 7 days
- **Format:** JSON array of messages

Example Redis key:
```
chatbot:user123:550e8400-e29b-41d4-a716-446655440000
```

## Troubleshooting

### Redis connection failed

**Error:** `Warning: Redis connection failed: ... Falling back to in-memory storage.`

**Solution:**
1. Check Redis is running: `docker ps | grep redis`
2. Test connection: `redis-cli -h localhost -p 6379 ping`
3. Verify REDIS_HOST=localhost in .env

### Qdrant connection failed

**Error:** `Error during retrieval: ...`

**Solution:**
1. Check Qdrant is running: `docker ps | grep qdrant`
2. Test connection: `curl http://localhost:6333/health`
3. Verify QDRANT_URL=http://localhost:6333 in .env

### Port already in use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 5001
lsof -i :5001  # On Mac/Linux
netstat -ano | findstr :5001  # On Windows

# Kill the process or change CHATBOT_SERVICE_PORT in .env
```

### Import errors

**Error:** `ModuleNotFoundError: No module named 'langgraph'`

**Solution:**
```bash
# Activate venv and install dependencies
source venv/bin/activate
pip install -r requirements.txt
```

## Development Workflow

1. **Start Docker services:**
   ```bash
   cd Prashiskshan_backend
   docker-compose up -d redis qdrant
   ```

2. **Start chatbot service:**
   ```bash
   cd Prashiskshan_ml/chatbot
   python chatbot_service_sse.py
   ```

3. **Start backend API:**
   ```bash
   cd Prashiskshan_backend
   npm run dev
   ```

4. **Start frontend:**
   ```bash
   cd Prashiskshan_frontend
   npm run dev
   ```

## Stopping Services

```bash
# Stop chatbot service
Ctrl+C in the terminal running chatbot_service_sse.py

# Stop Docker services
cd Prashiskshan_backend
docker-compose down
```

## Logs

The chatbot service logs to stderr:
- Initialization messages
- Pre-warming status
- Query processing
- Redis operations
- Errors and warnings

To save logs to a file:
```bash
python chatbot_service_sse.py 2>&1 | tee chatbot.log
```

## Performance

- **Cold start:** ~5-10 seconds (loading models)
- **Warm start:** Instant (models pre-loaded)
- **Query response:** 1-3 seconds (depends on LLM)
- **Memory usage:** ~500MB-1GB (embedding models)

## Production Deployment

For production, consider:
- Running chatbot service in Docker
- Using managed Redis (AWS ElastiCache, Redis Cloud)
- Using managed Qdrant (Qdrant Cloud)
- Adding monitoring and alerting
- Implementing auto-scaling
- Using production 
r (gunicorn) serveWSGI