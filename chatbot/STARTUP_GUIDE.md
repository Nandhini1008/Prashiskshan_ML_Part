# Chatbot Startup Guide

## Quick Start

Follow these steps in order to start the chatbot service:

### 1. Start Docker Services

```bash
cd Prashiskshan_backend
docker-compose up -d redis qdrant
```

Wait for services to be ready (~10 seconds).

### 2. Initialize Qdrant Collection

```bash
cd Prashiskshan_ml/chatbot
python init_qdrant.py
```

Expected output:

```
============================================================
Initializing Qdrant Collection
============================================================
Created new collection: internship_education_db
Collection size: 0 vectors

✅ Qdrant collection initialized successfully!

Collection Stats:
  - Name: internship_education_db
  - Documents: 0
  - Vector Size: 384
  - Distance Metric: COSINE
  - Qdrant URL: http://localhost:6333
============================================================
```

### 3. (Optional) Ingest Sample Data

If you have documents to ingest:

```bash
python ingestion/ingest_data.py
```

### 4. Start Chatbot Service

```bash
python chatbot_service_sse.py
```

Expected output:

```
Initializing RAG Chatbot components...
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Embedding model loaded successfully
Retriever initialized with collection: internship_education_db
Gemini LLM initialized: gemini-1.5-flash
RAG Chatbot initialized successfully!
🔥 Pre-warming RAG pipeline...
  → Loading sentence transformer into memory...
  ✓ Sentence transformer loaded
  → Warming up Qdrant connection...
  ✓ Qdrant connection warmed
✅ Pipeline pre-warmed in X.XXs
Starting SSE-enabled chatbot service on 0.0.0.0:5001
```

### 5. Test the Service

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

## Troubleshooting

### Issue 1: Gemini Model Not Found

**Error:**

```
Gemini API HTTP Error 404: models/gemini-2.0-flash-exp is not found
```

**Solution:**
The model name has been updated to `gemini-1.5-flash` in `config/settings.py`. Restart the chatbot service.

### Issue 2: Qdrant Collection Not Found

**Error:**

```
Collection `internship_education_db` doesn't exist!
```

**Solution:**
Run the initialization script:

```bash
python init_qdrant.py
```

### Issue 3: Redis Connection Failed

**Error:**

```
Warning: Redis connection failed: ... Falling back to in-memory storage.
```

**Solution:**

1. Check Redis is running:

   ```bash
   docker ps | grep redis
   ```

2. Test connection:

   ```bash
   docker exec -it prashiskshan_backend-redis-1 redis-cli ping
   ```

3. Verify `.env` has:
   ```
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

### Issue 4: Qdrant Connection Failed

**Error:**

```
Error initializing Qdrant client: ...
```

**Solution:**

1. Check Qdrant is running:

   ```bash
   docker ps | grep qdrant
   ```

2. Test connection:

   ```bash
   curl http://localhost:6333/health
   ```

3. Verify `.env` has:
   ```
   QDRANT_URL=http://localhost:6333
   ```

### Issue 5: Port Already in Use

**Error:**

```
Address already in use
```

**Solution:**
Find and kill the process using port 5001:

**Windows:**

```bash
netstat -ano | findstr :5001
taskkill /PID <PID> /F
```

**Mac/Linux:**

```bash
lsof -i :5001
kill -9 <PID>
```

Or change the port in `.env`:

```
CHATBOT_SERVICE_PORT=5002
```

## Environment Variables

Make sure your `.env` file in `Prashiskshan_ml/chatbot/` contains:

```bash
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
TOGETHER_API_KEY=your_together_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Qdrant Configuration (Docker)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Redis Configuration (Docker)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Chatbot Service Configuration
CHATBOT_SERVICE_PORT=5001
CHATBOT_SERVICE_HOST=0.0.0.0
MAX_CONVERSATION_HISTORY=10
```

## Complete Workflow

```bash
# 1. Start infrastructure
cd Prashiskshan_backend
docker-compose up -d redis qdrant

# 2. Initialize Qdrant
cd ../Prashiskshan_ml/chatbot
python init_qdrant.py

# 3. (Optional) Ingest data
python ingestion/ingest_data.py

# 4. Start chatbot
python chatbot_service_sse.py

# 5. In another terminal, start backend
cd ../../Prashiskshan_backend
npm run dev

# 6. In another terminal, start frontend
cd ../Prashiskshan_frontend
npm run dev
```

## Stopping Services

```bash
# Stop chatbot
Ctrl+C in the chatbot terminal

# Stop Docker services
cd Prashiskshan_backend
docker-compose down
```

## Logs and Debugging

### View Chatbot Logs

The chatbot logs to stderr. To save logs:

```bash
python chatbot_service_sse.py 2>&1 | tee chatbot.log
```

### View Docker Logs

```bash
# Redis logs
docker-compose logs -f redis

# Qdrant logs
docker-compose logs -f qdrant
```

### Check Qdrant Collection

```bash
# List collections
curl http://localhost:6333/collections

# Get collection info
curl http://localhost:6333/collections/internship_education_db
```

### Check Redis Data

```bash
# Connect to Redis
docker exec -it prashiskshan_backend-redis-1 redis-cli

# List chatbot keys
KEYS chatbot:*

# View a conversation
GET chatbot:user123:session456
```

## Performance Tips

1. **Pre-warming:** The chatbot pre-warms models on startup (~5-10 seconds)
2. **First query:** May take 2-3 seconds as models initialize
3. **Subsequent queries:** Should be faster (1-2 seconds)
4. **Memory usage:** ~500MB-1GB for embedding models

## Production Checklist

Before deploying to production:

- [ ] Set strong Redis password
- [ ] Use Qdrant Cloud or set API key
- [ ] Use production WSGI server (gunicorn)
- [ ] Set up monitoring and logging
- [ ] Configure auto-restart (systemd, supervisor)
- [ ] Set up health check endpoints
- [ ] Use environment-specific .env files
- [ ] Enable HTTPS
- [ ] Set up rate limiting
- [ ] Configure backup for Qdrant data

## Support

For issues:

1. Check this guide
2. Review error messages
3. Check Docker logs
4. Verify environment variables
5. Test individual components (Redis, Qdrant, Gemini API)
