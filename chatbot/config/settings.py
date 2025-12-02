"""
Configuration settings for the RAG chatbot system.
Manages API keys, model parameters, and system constants.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# API Configuration
TOGETHER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")  # Using OpenRouter instead
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# LLM Configuration
LLAMA_MODEL = "gemini-2.5-flash"
GEMINI_MODEL = "gemini-2.5-flash"

# LLM Parameters
LLAMA_TEMPERATURE = 0.3
LLAMA_MAX_TOKENS = 4096  # Increased from 1024
GEMINI_TEMPERATURE = 0.4
GEMINI_MAX_TOKENS = 8192  # Increased from 2048

# Vector Store Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)  # None for local, set for cloud
QDRANT_COLLECTION_NAME = "internship_education_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# Retrieval Configuration
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.50

# Chunking Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Intent Categories
INTENT_COMPANY_INTERNSHIP = "COMPANY_INTERNSHIP"
INTENT_EDUCATION_CODING = "EDUCATION_CODING"
INTENT_INTERVIEW_PREPARATION = "INTERVIEW_PREPARATION"
INTENT_GENERAL_EDUCATION = "GENERAL_EDUCATION"

# Routing Configuration
RAG_INTENTS = [INTENT_COMPANY_INTERNSHIP]
EXTERNAL_INTENTS = [
    INTENT_EDUCATION_CODING,
    INTENT_INTERVIEW_PREPARATION,
    INTENT_GENERAL_EDUCATION
]

# Data Paths
DATA_DIR = "data"
COMPANIES_DIR = os.path.join(DATA_DIR, "companies")
FAQS_DIR = os.path.join(DATA_DIR, "faqs")
COLLEGE_DOCS_DIR = os.path.join(DATA_DIR, "college_docs")

# Fallback Response
FALLBACK_RESPONSE = "Based on generally available information about internships and education programs, I can provide some guidance. However, specific details for this query are not in my current database. Please feel free to ask about general aspects or other companies/programs."

# Session Configuration
MAX_CONVERSATION_HISTORY = 10

def get_config() -> Dict[str, Any]:
    """
    Returns the complete configuration dictionary.
    
    Returns:
        Dict containing all configuration parameters
    """
    return {
        "together_api_key": TOGETHER_API_KEY,
        "gemini_api_key": GEMINI_API_KEY,
        "llama_model": LLAMA_MODEL,
        "gemini_model": GEMINI_MODEL,
        "llama_temperature": LLAMA_TEMPERATURE,
        "llama_max_tokens": LLAMA_MAX_TOKENS,
        "gemini_temperature": GEMINI_TEMPERATURE,
        "gemini_max_tokens": GEMINI_MAX_TOKENS,
        "qdrant_url": QDRANT_URL,
        "qdrant_api_key": QDRANT_API_KEY,
        "collection_name": QDRANT_COLLECTION_NAME,
        "embedding_model": EMBEDDING_MODEL,
        "top_k": TOP_K_RESULTS,
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "fallback_response": FALLBACK_RESPONSE,
        "max_conversation_history": MAX_CONVERSATION_HISTORY,
        "data_dir": DATA_DIR
    }

def validate_config() -> bool:
    """
    Validates that required API keys are set.
    
    Returns:
        True if configuration is valid, False otherwise
    """
    if not TOGETHER_API_KEY:
        print("Warning: OPENROUTER_API_KEY not set")
        return False
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set")
        return False
    return True
