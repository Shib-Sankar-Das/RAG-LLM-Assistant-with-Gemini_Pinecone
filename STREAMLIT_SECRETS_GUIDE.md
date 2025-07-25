# 🔑 Streamlit Secrets Configuration Guide

## Migration from .env to secrets.toml

This application now uses **Streamlit's native secrets management** instead of `.env` files for better security and deployment compatibility.

## ✅ Setup Instructions

### 1. Get Your API Keys

#### Pinecone API Key:
1. Go to **[Pinecone Console](https://app.pinecone.io/)**
2. **Sign in** to your account
3. Navigate to **"API Keys"** in the left sidebar
4. Either copy your existing valid key, or create a new API key

#### Google Gemini API Key:
1. Go to **[Google AI Studio](https://aistudio.google.com/)**
2. Sign in and navigate to "Get API Key"
3. Create a new API key or copy an existing one

### 2. Configure for Local Development

Create or update `.streamlit/secrets.toml` with your actual keys:

```toml
# Google Gemini API Configuration
GEMINI_API_KEY = "your_actual_gemini_api_key_here"

# Pinecone Configuration  
PINECONE_API_KEY = "your_actual_pinecone_api_key_here"
PINECONE_ENVIRONMENT = "gcp-starter"
PINECONE_INDEX_NAME = "rag-assistant"

# Model Configuration
MODEL_NAME = "gemini-2.5-pro"

# Optional: Override other settings if needed
CHUNK_SIZE = "1000"
CHUNK_OVERLAP = "200"
RETRIEVAL_K = "5"
```

### 3. Configure for Streamlit Cloud Deployment

1. Go to **Streamlit Cloud** → **Manage app** → **Settings** → **Secrets**
2. Add the same configuration in TOML format:

```toml
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
PINECONE_API_KEY = "your_actual_pinecone_api_key_here"
PINECONE_ENVIRONMENT = "gcp-starter"
PINECONE_INDEX_NAME = "rag-assistant"
MODEL_NAME = "gemini-2.5-pro"
```

## 🔧 Testing Your Configuration

Run your Streamlit app:
```bash
streamlit run app.py
```

Expected behavior:
- ✅ No authentication errors
- ✅ Successful connection to Pinecone
- ✅ Successful connection to Google Gemini

## 🚨 Important Security Notes

1. **Never commit secrets.toml** - It's already in `.gitignore`
2. **Use the template** - Copy from `.streamlit/secrets.toml.template`
3. **Keep keys secure** - Don't share or expose your API keys

## 🔄 Backward Compatibility

The application still supports `.env` files as a fallback, but **secrets.toml is recommended** for:
- Better Streamlit integration
- Enhanced security
- Easier deployment
- Cloud platform compatibility

## ⚡ Quick Setup

1. Copy the template:
   ```bash
   cp .streamlit/secrets.toml.template .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` with your actual API keys

3. Run the app:
   ```bash
   streamlit run app.py
   ```

---
*Updated: July 25, 2025 - Migrated to Streamlit secrets.toml*
