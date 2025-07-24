# Streamlit Cloud Secrets Configuration Guide

## 📋 How to Fix the 401 Unauthorized Error on Streamlit Cloud

### 🔍 Problem:
- Streamlit Cloud doesn't read `.env` files
- Your API keys are not being loaded, causing 401 Unauthorized errors
- The app works locally because it reads from your local `.env` file

### ✅ Solution: Configure Secrets in Streamlit Cloud

1. **Go to your Streamlit Cloud Dashboard:**
   - Visit: https://share.streamlit.io/
   - Find your deployed app: `rag-llm-assistant-with-gemini_pinecone`

2. **Click "Manage app" (bottom right of your app)**

3. **Go to "Settings" → "Secrets"**

4. **Add the following secrets in TOML format:**

```toml
# Streamlit Cloud Secrets (secrets.toml format)

# Gemini API Key
GEMINI_API_KEY = "AIzaSyBIMuR_AsYhB8r3u7hMOOFLHI2ayg8A36c"

# Pinecone Configuration
PINECONE_API_KEY = "pcsk_5NoZGp_FwLABPBqfhS8NR89yASJbQuf93yDPBNW4bdaurNgPsn6piVK7XZCjYxFFs6HiCu"
PINECONE_ENVIRONMENT = "gcp-starter"
PINECONE_INDEX_NAME = "rag-assistant"

# Model Configuration
MODEL_NAME = "gemini-2.5-pro"

# Database Configuration
DATABASE_TYPE = "pinecone"

# Text Processing Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Embeddings Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cpu"

# Retrieval Configuration
RETRIEVAL_K = 5

# Web Scraping Configuration
MAX_PAGES_DEFAULT = 3
MAX_PAGES_LIMIT = 10
REQUEST_TIMEOUT = 10

# Chat History Configuration
CHAT_HISTORY_ENABLED = true
MAX_CHAT_HISTORY_CONTEXT = 5
FEEDBACK_ENABLED = true
FEEDBACK_WEIGHT = 0.2
```

5. **Click "Save" to apply the secrets**

6. **Restart your app** (the app will automatically restart when you save secrets)

### 🔧 Alternative: Update Code to Handle Missing Secrets

If you want to make your code more robust, you can also update your config.py to handle missing environment variables gracefully.

### ⚠️ Important Notes:
- Use TOML format in Streamlit Cloud secrets (with quotes around strings)
- Use regular .env format in your local .env file (without quotes)
- Never commit API keys to your GitHub repository
- Always use the secrets management system for cloud deployments

### 🚀 After Setup:
Your Streamlit Cloud app should work exactly like your local version once the secrets are configured properly!
