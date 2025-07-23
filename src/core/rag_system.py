"""
Main RAG system implementation.
"""

import os
import shutil
from datetime import datetime
from typing import List, Optional
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.schema import Document

# Import Pinecone vector store
try:
    from langchain_pinecone import PineconeVectorStore
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    st.error("Pinecone packages not available. Please install: pip install pinecone-client langchain-pinecone")

from .llm import GeminiLLM
from .document_processor import WebScraper, PDFProcessor
from ..config import Config

class RAGSystem:
    """Main RAG system class."""
    
    def __init__(self, api_key: str):
        """Initialize the RAG system.
        
        Args:
            api_key: Google Gemini API key
        """
        self.config = Config()
        self.api_key = api_key
        self.llm = GeminiLLM(api_key, self.config.MODEL_NAME)
        
        # Initialize embeddings
        self.embeddings = self._initialize_embeddings_robust()
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len
        )
        
        # Initialize processors
        self.web_scraper = WebScraper()
        self.pdf_processor = PDFProcessor()
        
        # Initialize storage
        self.vectorstore = None
        self.qa_chain = None
        self.sources = []
        
        # Database type - always Pinecone
        self.db_type = "pinecone"
        
    def _initialize_embeddings_robust(self):
        """Initialize embeddings with multiple fallback strategies."""
        embedding_strategies = [
            # Strategy 1: Use configured device
            {
                'model_name': self.config.EMBEDDING_MODEL,
                'model_kwargs': {'device': self.config.EMBEDDING_DEVICE},
                'description': f"Using {self.config.EMBEDDING_DEVICE} device"
            },
            # Strategy 2: Force CPU
            {
                'model_name': self.config.EMBEDDING_MODEL,
                'model_kwargs': {'device': 'cpu'},
                'description': "Falling back to CPU"
            },
            # Strategy 3: No device specification
            {
                'model_name': self.config.EMBEDDING_MODEL,
                'model_kwargs': {},
                'description': "Using default device"
            },
            # Strategy 4: Different model on CPU
            {
                'model_name': "sentence-transformers/all-MiniLM-L6-v2",
                'model_kwargs': {'device': 'cpu'},
                'description': "Using fallback model on CPU"
            },
            # Strategy 5: Minimal configuration
            {
                'model_name': "sentence-transformers/all-MiniLM-L6-v2",
                'model_kwargs': {},
                'description': "Using minimal configuration"
            }
        ]
        
        for i, strategy in enumerate(embedding_strategies):
            try:
                if i > 0:  # Show warning for fallback strategies
                    st.warning(f"⚠️ {strategy['description']}")
                
                embeddings = HuggingFaceEmbeddings(
                    model_name=strategy['model_name'],
                    model_kwargs=strategy['model_kwargs']
                )
                
                if i == 0:
                    st.success(f"✅ Embeddings initialized successfully with {strategy['description']}")
                else:
                    st.info(f"✅ Embeddings initialized with fallback: {strategy['description']}")
                
                return embeddings
                
            except Exception as e:
                if i == len(embedding_strategies) - 1:  # Last strategy failed
                    st.error(f"❌ All embedding initialization strategies failed. Last error: {str(e)}")
                    raise e
                else:
                    st.warning(f"⚠️ Strategy {i+1} failed: {str(e)[:100]}...")
                    continue
        
        raise RuntimeError("Failed to initialize embeddings with any strategy")
    
    def setup_vectorstore(self, namespace: Optional[str] = None):
        """Initialize Pinecone vector store.
        
        Args:
            namespace: Pinecone namespace for organization (None for default, "temp" for temporary)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self._setup_pinecone_vectorstore(namespace)
                
        except Exception as e:
            st.error(f"Error setting up vectorstore: {str(e)}")
            return False
    
    def _setup_pinecone_vectorstore(self, namespace: Optional[str] = None):
        """Initialize Pinecone vector store.
        
        Args:
            namespace: Pinecone namespace for organization (None for default, "temp" for temporary)
        """
        if not PINECONE_AVAILABLE:
            st.error("Pinecone is not available. Please install: pip install pinecone-client langchain-pinecone")
            return False
        
        try:
            # Initialize Pinecone
            pc = Pinecone(api_key=self.config.PINECONE_API_KEY)
            
            # Check if index exists, create if not
            index_name = self.config.PINECONE_INDEX_NAME
            indexes = pc.list_indexes()
            existing_index_names = [index.name for index in indexes]
            
            if index_name not in existing_index_names:
                st.info(f"🆕 Creating new Pinecone index: {index_name}")
                
                # Create index using ServerlessSpec for AWS free tier
                pc.create_index(
                    name=index_name,
                    dimension=384,  # dimension for all-MiniLM-L6-v2
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                st.success(f"✅ Created new Pinecone index: {index_name}")
                
                # Wait for index to be ready
                import time
                with st.spinner("⏳ Waiting for index to be ready..."):
                    time.sleep(10)
            else:
                if namespace == "temp":
                    st.success(f"🚀 Connected to Pinecone index: {index_name} (temporary namespace)")
                else:
                    st.success(f"📂 Connected to existing Pinecone index: {index_name}")
            
            # Initialize vector store with namespace
            self.vectorstore = PineconeVectorStore(
                index_name=index_name,
                embedding=self.embeddings,
                namespace=namespace or "default"
            )
            
            # Setup QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(
                    search_kwargs={"k": self.config.RETRIEVAL_K}
                ),
                return_source_documents=True
            )
            
            return True
            
        except Exception as e:
            st.error(f"Failed to setup Pinecone: {str(e)}")
            return False
    
    def scrape_website(self, url: str, max_pages: Optional[int] = None) -> List[Document]:
        """Scrape website content.
        
        Args:
            url: Website URL to scrape
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of Document objects
        """
        if max_pages is None:
            max_pages = self.config.MAX_PAGES_DEFAULT
            
        return self.web_scraper.scrape_website(url, max_pages)
    
    def process_pdf(self, pdf_file) -> List[Document]:
        """Process PDF file.
        
        Args:
            pdf_file: Streamlit uploaded file object
            
        Returns:
            List of Document objects
        """
        return self.pdf_processor.process_pdf(pdf_file)
    
    def add_documents_to_vectorstore(self, documents: List[Document]):
        """Add documents to ChromaDB with text splitting.
        
        Args:
            documents: List of Document objects to add
        """
        if not documents:
            st.warning("No documents to add")
            return
        
        try:
            if self.vectorstore is None:
                st.error("Vectorstore is not initialized. Please set up the vectorstore first.")
                return
                
            with st.spinner("Adding documents to vector database..."):
                # Split documents into chunks
                split_docs = self.text_splitter.split_documents(documents)
                
                # Add to vectorstore
                self.vectorstore.add_documents(split_docs)
                
                # Note: persist() is no longer needed as docs are automatically persisted in Chroma 0.4.x+
                
                # Update sources
                for doc in documents:
                    source_info = {
                        "source": doc.metadata.get("source", "Unknown"),
                        "type": doc.metadata.get("type", "Unknown"),
                        "added_at": datetime.now().isoformat()
                    }
                    if source_info not in self.sources:
                        self.sources.append(source_info)
                
                st.success(f"Added {len(split_docs)} document chunks to the database")
                
        except Exception as e:
            st.error(f"Error adding documents: {str(e)}")
    
    def query(self, question: str) -> dict:
        """Query the RAG system.
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and source documents
        """
        if not self.qa_chain:
            return {"error": "System not initialized"}
        
        try:
            with st.spinner("Searching for relevant information..."):
                result = self.qa_chain.invoke({"query": question})
                
                return {
                    "answer": result["result"],
                    "source_documents": result["source_documents"]
                }
                
        except Exception as e:
            return {"error": f"Query error: {str(e)}"}
    
    def clear_database(self, namespace: Optional[str] = None):
        """Clear the Pinecone vector database.
        
        Args:
            namespace: Specific namespace to clear (None for all)
        """
        try:
            if self.vectorstore and PINECONE_AVAILABLE:
                pc = Pinecone(api_key=self.config.PINECONE_API_KEY)
                index = pc.Index(self.config.PINECONE_INDEX_NAME)
                
                if namespace:
                    # Clear specific namespace
                    index.delete(delete_all=True, namespace=namespace)
                    st.success(f"Pinecone namespace '{namespace}' cleared successfully")
                else:
                    # Clear all namespaces
                    index.delete(delete_all=True)
                    st.success("Pinecone index cleared successfully")
                
            self.vectorstore = None
            self.qa_chain = None
            self.sources = []
            
        except Exception as e:
            st.error(f"Error clearing database: {str(e)}")
    
    def get_database_stats(self) -> dict:
        """Get Pinecone database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        if not self.vectorstore:
            return {"document_count": 0, "source_count": 0, "database_type": "pinecone"}
        
        try:
            # For Pinecone, get stats from the index
            if PINECONE_AVAILABLE:
                pc = Pinecone(api_key=self.config.PINECONE_API_KEY)
                index = pc.Index(self.config.PINECONE_INDEX_NAME)
                stats = index.describe_index_stats()
                document_count = stats.get('total_vector_count', 0)
            else:
                # Fallback estimation
                document_count = len(self.sources) * 10
                
            source_count = len(self.sources)
            
            return {
                "document_count": document_count,
                "source_count": source_count,
                "sources": self.sources,
                "database_type": "pinecone"
            }
        except Exception:
            return {"document_count": 0, "source_count": 0, "database_type": "pinecone"}
