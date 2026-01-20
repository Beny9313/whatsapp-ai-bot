"""
Embeddings using OpenAI API (high quality semantic search).
Cost: ~$0.13 per 1M tokens (~$6 one-time for 46K chunks)
"""

import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class OpenAIEmbeddings:
	"""
	OpenAI embeddings via API.
	
	Model: text-embedding-3-small (1536 dimensions)
	Quality: Excellent semantic search
	Cost: $0.00002 per 1K tokens
	"""
	
	def __init__(self, model: str = "text-embedding-3-small"):
		api_key = os.getenv("OPENAI_API_KEY")
		if not api_key:
			raise ValueError("OPENAI_API_KEY not found in .env file")
		
		self.client = OpenAI(api_key=api_key)
		self.model = model
		print(f"🔑 Using OpenAI embeddings: {model}")
	
	def embed_documents(self, texts: List[str]) -> List[List[float]]:
		"""Embed multiple documents in batches"""
		
		# OpenAI batch size limit
		BATCH_SIZE = 1000
		all_embeddings = []
		
		for i in range(0, len(texts), BATCH_SIZE):
			batch = texts[i:i + BATCH_SIZE]
			batch_num = (i // BATCH_SIZE) + 1
			total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE
			
			print(f"   📤 Embedding batch {batch_num}/{total_batches} ({len(batch)} texts)...")
			
			response = self.client.embeddings.create(
				model=self.model,
				input=batch
			)
			
			batch_embeddings = [item.embedding for item in response.data]
			all_embeddings.extend(batch_embeddings)
		
		return all_embeddings
	
	def embed_query(self, text: str) -> List[float]:
		"""Embed a single query"""
		
		response = self.client.embeddings.create(
			model=self.model,
			input=[text]
		)
		
		return response.data[0].embedding


def get_embeddings():
	"""Get embeddings instance (OpenAI or fallback to lightweight)"""
	
	if os.getenv("OPENAI_API_KEY"):
		try:
			return OpenAIEmbeddings()
		except Exception as e:
			print(f"⚠️  OpenAI embeddings failed: {e}")
			print("   Falling back to lightweight embeddings")
			from .embeddings_lightweight import LightweightEmbeddings
			return LightweightEmbeddings()
	else:
		print("⚠️  OPENAI_API_KEY not set. Using lightweight embeddings.")
		from .embeddings_lightweight import LightweightEmbeddings
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
	print(f"✅ Sample: {doc_embeddings[0][:5]}")