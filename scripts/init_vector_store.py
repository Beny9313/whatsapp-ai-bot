"""
Initialize vector store on first Railway deployment.
Run once after deployment to index documents.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.document_loader import SAPDocumentLoader
from src.rag.vector_store import SAPVectorStore

def init():
    print("🚀 Initializing vector store on Railway...")
    
    # Load documents
    loader = SAPDocumentLoader()
    chunks = loader.prepare_for_vectorstore()
    
    if not chunks:
        print("❌ No documents found!")
        return
    
    # Create vector store
    vector_store = SAPVectorStore()
    vector_store.reset()
    vector_store.add_documents(chunks)
    
    print(f"✅ Vector store ready with {len(chunks)} chunks")

if __name__ == "__main__":
    init()