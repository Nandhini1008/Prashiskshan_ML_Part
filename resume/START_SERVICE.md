# Starting the Resume Processing ML Service

The ML service must be running for resume upload and analysis to work.

## Quick Start (Windows)

1. Open a terminal in the `Prashiskshan_ml/resume` directory
2. Run:
   ```bash
   start_api_server.bat
   ```

## Quick Start (Linux/Mac)

1. Open a terminal in the `Prashiskshan_ml/resume` directory
2. Make the script executable:
   ```bash
   chmod +x start_api_server.sh
   ```
3. Run:
   ```bash
   ./start_api_server.sh
   ```

## Manual Start

If the scripts don't work, you can start the service manually:

1. **Activate virtual environment** (if you have one):
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server**:
   ```bash
   python api_server.py
   ```

## Verify Service is Running

Once started, you should see:
```
============================================================
🚀 Resume Processing API Server
============================================================
📍 Running on: http://0.0.0.0:8002
📚 API Docs: http://0.0.0.0:8002/docs
============================================================
```

You can test it by visiting:
- Health check: http://localhost:8002/health
- API docs: http://localhost:8002/docs

## Environment Variables

Make sure you have a `.env` file in the `Prashiskshan_ml/resume` directory with:
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Troubleshooting

### Port 8002 already in use
If you get a port conflict error, you can change the port by setting an environment variable:
```bash
# Windows
set PORT=8003
python api_server.py

# Linux/Mac
export PORT=8003
python api_server.py
```

Then update the Node.js backend `.env` file:
```
ML_RESUME_SERVICE_URL=http://localhost:8003
```

### Connection refused error
- Make sure the ML service is running on port 8002
- Check that the Node.js backend has the correct `ML_RESUME_SERVICE_URL` in its `.env` file
- Verify there are no firewall issues blocking the connection

