"""
Configuration settings for the RAG LLM Assistant.
"""

import os
from dotenv import load_dotenv 

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the RAG application."""
    
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")  # free tier environment
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rag-assistant")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-pro")
    
    # Database Configuration
    DATABASE_TYPE = "pinecone"  # Always use Pinecone
    DEFAULT_PERSIST_DIR = "./chroma_db"  # Legacy - not used anymore
    
    # Text Processing Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Embeddings Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")  # Default to CPU to avoid meta tensor issues
    
    # Retrieval Configuration
    RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "5"))
    
    # Web Scraping Configuration
    MAX_PAGES_DEFAULT = int(os.getenv("MAX_PAGES_DEFAULT", "3"))
    MAX_PAGES_LIMIT = int(os.getenv("MAX_PAGES_LIMIT", "10"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
    
    # UI Configuration
    APP_TITLE = "RAG LLM Assistant"
    APP_ICON = "🤖"
    
    # Chat History Configuration
    CHAT_HISTORY_ENABLED = os.getenv("CHAT_HISTORY_ENABLED", "true").lower() == "true"
    MAX_CHAT_HISTORY_CONTEXT = int(os.getenv("MAX_CHAT_HISTORY_CONTEXT", "5"))
    FEEDBACK_ENABLED = os.getenv("FEEDBACK_ENABLED", "true").lower() == "true"
    FEEDBACK_WEIGHT = float(os.getenv("FEEDBACK_WEIGHT", "0.2"))
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration settings."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required. Please set it in your .env file.")
        
        if not cls.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is required. Please set it in your .env file.")
        
        return True
