"""
SSE-enabled persistent HTTP service for the RAG chatbot.
Implements Server-Sent Events for streaming responses.
Pre-warms the RAG pipeline at startup.
"""

from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import RAGChatbot

app = Flask(__name__)
CORS(app)

chatbot = None
is_warmed_up = False


def pre_warm_pipeline(bot):
    """Pre-warm the RAG pipeline at startup to eliminate cold-start latency."""
    global is_warmed_up
    if is_warmed_up:
        return
    
    print("🔥 Pre-warming RAG pipeline...", file=sys.stderr)
    start_time = time.time()
    
    try:
        print("  → Loading sentence transformer into memory...", file=sys.stderr)
        dummy_text = "This is a warm-up query to load the embedding model"
        bot.retriever.embedder.encode([dummy_text])
        print("  ✓ Sentence transformer loaded", file=sys.stderr)
        
        print("  → Warming up Qdrant ANN indexes...", file=sys.stderr)
        bot.retriever.retrieve(dummy_text)
        print("  ✓ Qdrant indexes warmed", file=sys.stderr)
        
        elapsed = time.time() - start_time
        print(f"✅ Pipeline pre-warmed in {elapsed:.2f}s", file=sys.stderr)
        is_warmed_up = True
        
    except Exception as e:
        print(f"⚠️  Pre-warming failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

def initialize_chatbot():
    """Initialize the chatbot instance (called once at startup)."""
    global chatbot
    if chatbot is None:
        print("Initializing chatbot service...", file=sys.stderr)
        chatbot = RAGChatbot()
        print("Chatbot service ready!", file=sys.stderr)
        pre_warm_pipeline(chatbot)
    return chatbot

def chunk_text(text, chunk_size=30):
    """Split text into semantic chunks for streaming."""
    if not text:
        return
    
    sentences = text.replace('? ', '?|').replace('! ', '!|').replace('. ', '.|').split('|')
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        if current_chunk and len(current_chunk) + len(sentence) > chunk_size:
            yield current_chunk
            current_chunk = sentence + " "
        else:
            current_chunk += sentence + " "
    
    if current_chunk.strip():
        yield current_chunk.strip()


def generate_sse_response(query_text, user_id, session_id):
    """Generator function for SSE streaming."""
    try:
        bot = initialize_chatbot()
        yield f"data: {json.dumps({'type': 'start'})}\n\n"
        
        full_response = bot.query(query_text, user_id, session_id)
        
        for chunk in chunk_text(full_response, chunk_size=30):
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            time.sleep(0.01)
        
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "chatbot_initialized": chatbot is not None,
        "pipeline_warmed": is_warmed_up
    })

@app.route('/query', methods=['POST'])
def query():
    """Handle chatbot query - returns JSON (for Node.js backend compatibility)."""
    try:
        data = request.json
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        query_text = data.get('query')
        
        if not user_id or not session_id:
            return jsonify({"error": "user_id and session_id are required"}), 400
        
        if not query_text or not query_text.strip():
            return jsonify({"error": "query is required"}), 400
        
        # Get full response (non-streaming for Node.js backend)
        bot = initialize_chatbot()
        response = bot.query(query_text, user_id, session_id)
        
        return jsonify({
            "success": True,
            "response": response,
            "sessionId": session_id
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query-stream', methods=['POST'])
def query_stream():
    """Handle chatbot query with SSE streaming (for frontend direct access)."""
    try:
        data = request.json
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        query_text = data.get('query')
        
        if not user_id or not session_id:
            return jsonify({"error": "user_id and session_id are required"}), 400
        
        if not query_text or not query_text.strip():
            return jsonify({"error": "query is required"}), 400
        
        return Response(
            generate_sse_response(query_text, user_id, session_id),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_session():
    """Clear conversation session."""
    try:
        data = request.json
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id or not session_id:
            return jsonify({"error": "user_id and session_id are required"}), 400
        
        bot = initialize_chatbot()
        bot.clear_session(user_id, session_id)
        
        return jsonify({"success": True, "message": "Session cleared"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.after_request
def after_request(response):
    """Disable buffering for SSE responses."""
    if response.mimetype == 'text/event-stream':
        response.headers['X-Accel-Buffering'] = 'no'
    return response

if __name__ == '__main__':
    initialize_chatbot()
    port = int(os.getenv('CHATBOT_SERVICE_PORT', 5001))
    host = os.getenv('CHATBOT_SERVICE_HOST', '0.0.0.0')
    print(f"Starting SSE-enabled chatbot service on {host}:{port}", file=sys.stderr)
    app.run(host=host, port=port, debug=False, threaded=True)
