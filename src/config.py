"""
Configuration settings for the RAG LLM Assistant.
"""

import os
import streamlit as st

def get_config_value(key: str, default: str = None):
    """Get configuration value from Streamlit secrets or environment variables."""
    try:
        # Try to get from Streamlit secrets first
        if hasattr(st, 'secrets') and st.secrets is not None:
            if key in st.secrets:
                return st.secrets[key]
        # Fallback to environment variables (for backward compatibility)
        import os
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(key, default)
    except Exception:
        # If secrets are not available, use environment variables
        import os
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(key, default)

class Config:
    """Configuration class for the RAG application."""
    
    # API Configuration
    GEMINI_API_KEY = get_config_value("GEMINI_API_KEY")
    PINECONE_API_KEY = get_config_value("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = get_config_value("PINECONE_ENVIRONMENT", "gcp-starter")
    PINECONE_INDEX_NAME = get_config_value("PINECONE_INDEX_NAME", "rag-assistant")
    MODEL_NAME = get_config_value("MODEL_NAME", "gemini-2.5-pro")
    
    # Database Configuration
    DATABASE_TYPE = "pinecone"  # Always use Pinecone
    DEFAULT_PERSIST_DIR = "./chroma_db"  # Legacy - not used anymore
    
    # Text Processing Configuration
    CHUNK_SIZE = int(get_config_value("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(get_config_value("CHUNK_OVERLAP", "200"))
    
    # Embeddings Configuration
    EMBEDDING_MODEL = get_config_value("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DEVICE = get_config_value("EMBEDDING_DEVICE", "cpu")
    
    # Retrieval Configuration
    RETRIEVAL_K = int(get_config_value("RETRIEVAL_K", "5"))
    
    # Web Scraping Configuration
    MAX_PAGES_DEFAULT = int(get_config_value("MAX_PAGES_DEFAULT", "3"))
    MAX_PAGES_LIMIT = int(get_config_value("MAX_PAGES_LIMIT", "10"))
    REQUEST_TIMEOUT = int(get_config_value("REQUEST_TIMEOUT", "10"))
    
    # UI Configuration
    APP_TITLE = "RAG LLM Assistant"
    APP_ICON = "🤖"
    
    # Chat History Configuration
    CHAT_HISTORY_ENABLED = get_config_value("CHAT_HISTORY_ENABLED", "true").lower() == "true"
    MAX_CHAT_HISTORY_CONTEXT = int(get_config_value("MAX_CHAT_HISTORY_CONTEXT", "5"))
    FEEDBACK_ENABLED = get_config_value("FEEDBACK_ENABLED", "true").lower() == "true"
    FEEDBACK_WEIGHT = float(get_config_value("FEEDBACK_WEIGHT", "0.2"))
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration settings."""
        # Check if running in Streamlit (secrets available)
        is_streamlit_app = hasattr(st, 'secrets')
        
        if not cls.GEMINI_API_KEY:
            if is_streamlit_app:
                raise ValueError("❌ GEMINI_API_KEY is missing. Please add it to .streamlit/secrets.toml:\n"
                               "[default]\n"
                               "GEMINI_API_KEY = \"your_key_here\"")
            else:
                raise ValueError("❌ GEMINI_API_KEY is required. Please set it in .streamlit/secrets.toml or .env file.")
        
        if not cls.PINECONE_API_KEY:
            if is_streamlit_app:
                raise ValueError("❌ PINECONE_API_KEY is missing. Please add it to .streamlit/secrets.toml:\n"
                               "[default]\n"
                               "PINECONE_API_KEY = \"your_key_here\"")
            else:
                raise ValueError("❌ PINECONE_API_KEY is required. Please set it in .streamlit/secrets.toml or .env file.")
        
        # Validate API key format
        if len(cls.PINECONE_API_KEY) < 50:
            raise ValueError(f"❌ PINECONE_API_KEY appears to be truncated or invalid.\n"
                           f"Current length: {len(cls.PINECONE_API_KEY)} characters\n"
                           f"Expected: 50+ characters\n"
                           f"Please check your API key in {'.streamlit/secrets.toml' if is_streamlit_app else '.env file'}")
        
        # Check API key format (Pinecone keys typically start with 'pcsk_')
        if not cls.PINECONE_API_KEY.startswith('pcsk_'):
            raise ValueError(f"❌ PINECONE_API_KEY format appears invalid.\n"
                           f"Pinecone API keys should start with 'pcsk_'\n"
                           f"Current key starts with: '{cls.PINECONE_API_KEY[:10]}...'\n"
                           f"Please verify your API key in {'.streamlit/secrets.toml' if is_streamlit_app else '.env file'}")
        
        return True
