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
        missing_vars = []
        
        if not cls.GEMINI_API_KEY:
            missing_vars.append("GEMINI_API_KEY")
        
        if not cls.PINECONE_API_KEY:
            missing_vars.append("PINECONE_API_KEY")
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}\n\n"
            
            # Check if running on Streamlit Cloud
            if os.getenv("STREAMLIT_SHARING_MODE") or "share.streamlit.io" in os.getenv("STREAMLIT_SERVER_ADDRESS", ""):
                error_msg += "🌐 You're running on Streamlit Cloud. Please configure secrets:\n"
                error_msg += "1. Go to your app dashboard\n"
                error_msg += "2. Click 'Manage app' → 'Settings' → 'Secrets'\n"
                error_msg += "3. Add your API keys in TOML format:\n"
                error_msg += "   GEMINI_API_KEY = \"your_key_here\"\n"
                error_msg += "   PINECONE_API_KEY = \"your_key_here\"\n"
            else:
                error_msg += "💻 For local development, add these to your .env file:\n"
                for var in missing_vars:
                    error_msg += f"   {var}=your_key_here\n"
            
            raise ValueError(error_msg)
        
        return True
