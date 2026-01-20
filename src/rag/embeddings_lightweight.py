"""
Lightweight embeddings - no heavy model downloads.
Uses simple text hashing (fine for learning/testing).

For production, use: OpenAI, Cohere, or Voyage AI embeddings API.
"""

import hashlib
from typing import List


class LightweightEmbeddings:
    """
    Simple deterministic embeddings using text hashing.
    
    ✅ Pros:
    - Zero disk space (no model download)
    - Instant (no GPU needed)
    - Deterministic (same text = same embedding)
    - Good enough for learning/testing
    
    ❌ Cons:
    - Lower semantic quality than real embeddings
    - Not suitable for production
    
    For production, replace with:
    - OpenAI: text-embedding-3-small (~$0.02 per 1M tokens)
    - Cohere: embed-english-v3.0
    - Voyage AI: voyage-2
    """
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        return [self._embed_text(text) for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self._embed_text(text)
    
    def _embed_text(self, text: str) -> List[float]:
        """Create embedding from text using hash"""
        
        # Hash the text
        text_hash = hashlib.sha512(text.lower().encode()).hexdigest()
        
        # Convert hash to float vector
        embedding = []
        for i in range(0, len(text_hash), 2):
            val = int(text_hash[i:i+2], 16) / 128.0 - 1.0
            embedding.append(val)
        
        # Pad or trim to dimension
        while len(embedding) < self.dimension:
            embedding.append(0.0)
        
        return embedding[:self.dimension]


def get_embeddings():
    """Get embeddings instance"""
    print("ℹ️  Using lightweight embeddings (no model download)")
    return LightweightEmbeddings()


if __name__ == "__main__":
    embeddings = get_embeddings()
    
    test_texts = [
        "Service Cloud ticket configuration",
        "CPI integration setup",
        "How to configure tickets?"
    ]
    
    print("\n📊 Testing embeddings...")
    doc_embeddings = embeddings.embed_documents(test_texts[:2])
    query_embedding = embeddings.embed_query(test_texts[2])
    
    print(f"✅ Doc embeddings: {len(doc_embeddings)} x {len(doc_embeddings[0])} dims")
    print(f"✅ Query embedding: {len(query_embedding)} dims")
    print(f"✅ Sample values: {doc_embeddings[0][:5]}")