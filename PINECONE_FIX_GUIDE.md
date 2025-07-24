# 🔑 Pinecone API Key Setup Guide

## Problem
You're getting a "401 Unauthorized - Invalid API Key" error when connecting to Pinecone.

## Root Cause
Your current Pinecone API key is either:
- Expired or revoked
- From a different Pinecone project
- Has formatting issues

## ✅ Solution Steps

### 1. Get a New API Key
1. Go to **[Pinecone Console](https://app.pinecone.io/)**
2. **Sign in** to your account
3. Navigate to **"API Keys"** in the left sidebar
4. Either:
   - **Copy your existing valid key**, or
   - **Create a new API key** by clicking "Create API Key"

### 2. Update Your Environment Files

#### For Local Development (.env file):
```bash
# Update this line in your .env file:
PINECONE_API_KEY=your_new_api_key_here
```

#### For Streamlit Cloud Deployment:
1. Go to **Streamlit Cloud** → **Manage app** → **Settings** → **Secrets**
2. Update the secrets with:
```toml
PINECONE_API_KEY = "your_new_api_key_here"
PINECONE_ENVIRONMENT = "gcp-starter"
PINECONE_INDEX_NAME = "rag-assistant"
GEMINI_API_KEY = "your_gemini_api_key"
```

### 3. Verify the Fix
Run this test command:
```bash
python pinecone_test.py
```

Expected output:
```
✅ Pinecone connection successful!
📊 Available indexes: ['rag-assistant']
```

### 4. Check Your Index
Make sure you have an index named `rag-assistant` in your Pinecone project:
- **Dimensions**: 384 (for sentence-transformers/all-MiniLM-L6-v2)
- **Metric**: cosine
- **Environment**: gcp-starter (free tier)

## 🚨 Important Notes

1. **Keep your API key secure** - never commit it to git
2. **Free tier limitations** - gcp-starter environment has usage limits
3. **Index creation** - if you don't have the 'rag-assistant' index, create one with:
   - Dimensions: 384
   - Metric: cosine
   - Environment: gcp-starter

## Next Steps
1. Update your API key as described above
2. Test the connection with `python pinecone_test.py`
3. If successful, run your main app with `streamlit run app.py`

---
*Generated on: July 24, 2025*
