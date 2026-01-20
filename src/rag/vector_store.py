"""
ChromaDB vector store with domain-filtered retrieval.
SOLVES: Cross-domain query problem from Day 2!
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from langchain_core.documents import Document

from .embeddings import get_embeddings


class SAPVectorStore:
	"""
	Vector store for SAP documentation.
	Supports single-domain AND multi-domain retrieval.
	"""
	
	def __init__(self, persist_directory: str = "./vector_store"):
		self.persist_directory = persist_directory
		self.embeddings = get_embeddings()
		
		# Create directory
		Path(persist_directory).mkdir(parents=True, exist_ok=True)
		
		# Initialize ChromaDB
		self.client = chromadb.PersistentClient(
			path=persist_directory,
			settings=Settings(
				anonymized_telemetry=False,
				allow_reset=True
			)
		)
		
		self.collection_name = "sap_cx_docs"
		
		# Get or create collection
		try:
			self.collection = self.client.get_collection(self.collection_name)
			print(f"✅ Loaded collection: {self.collection.count()} docs")
		except:
			self.collection = self.client.create_collection(
				name=self.collection_name,
				metadata={"description": "SAP CX documentation"}
			)
			print(f"✅ Created collection: {self.collection_name}")
	
	def add_documents(self, documents: List[Document]) -> None:
		"""Add documents to vector store in batches"""
		
		if not documents:
			print("⚠️  No documents to add")
			return
		
		print(f"\n📥 Adding {len(documents)} documents...")
		
		# ChromaDB batch size limit
		BATCH_SIZE = 5000
		total_docs = len(documents)
		
		for i in range(0, total_docs, BATCH_SIZE):
			batch = documents[i:i + BATCH_SIZE]
			batch_num = (i // BATCH_SIZE) + 1
			total_batches = (total_docs + BATCH_SIZE - 1) // BATCH_SIZE
			
			print(f"📦 Batch {batch_num}/{total_batches}: Processing {len(batch)} documents...")
			
			# Prepare batch data
			batch_ids = [f"doc_{i + j}" for j in range(len(batch))]
			batch_texts = [doc.page_content for doc in batch]
			batch_metadatas = [doc.metadata for doc in batch]
			
			# Create embeddings for batch
			print(f"   🔢 Creating embeddings...")
			batch_embeddings = self.embeddings.embed_documents(batch_texts)
			
			# Add batch to ChromaDB
			self.collection.add(
				ids=batch_ids,
				documents=batch_texts,
				embeddings=batch_embeddings,
				metadatas=batch_metadatas
			)
			
			print(f"   ✅ Batch {batch_num}/{total_batches} added")
		
		print(f"\n✅ COMPLETE: Added {len(documents)} documents in {total_batches} batches")
		print(f"📊 Total in collection: {self.collection.count()}")
	
	def search(
		self, 
		query: str, 
		domain_filter: Optional[str] = None,
		top_k: int = 5
	) -> List[Dict]:
		"""
		Search vector store with optional domain filtering.
		
		Args:
			query: Search query
			domain_filter: Filter by domain (e.g., "service_cloud")
			top_k: Number of results
		
		Returns:
			List of matching documents
		"""
		
		query_embedding = self.embeddings.embed_query(query)
		
		# Build filter
		where_filter = {"domain": domain_filter} if domain_filter else None
		
		# Search
		results = self.collection.query(
			query_embeddings=[query_embedding],
			n_results=top_k,
			where=where_filter
		)
		
		# Format results
		documents = []
		if results['documents'] and results['documents'][0]:
			for i, doc_text in enumerate(results['documents'][0]):
				documents.append({
					"content": doc_text,
					"metadata": results['metadatas'][0][i],
					"distance": results['distances'][0][i]
				})
		
		return documents
	
	def search_multi_domain(
		self,
		query: str,
		domains: List[str],
		top_k_per_domain: int = 3
	) -> List[Dict]:
		"""
		THE FIX for cross-domain queries!
		
		Search across multiple domains (e.g., Service Cloud + CPI).
		
		Args:
			query: Search query
			domains: List of domains to search
			top_k_per_domain: Results per domain
		
		Returns:
			Combined results from all domains
		"""
		
		all_results = []
		
		print(f"🔍 Multi-domain search: {domains}")
		
		for domain in domains:
			domain_results = self.search(
				query=query,
				domain_filter=domain,
				top_k=top_k_per_domain
			)
			
			print(f"  {domain}: {len(domain_results)} results")
			all_results.extend(domain_results)
		
		return all_results
	
	def reset(self):
		"""Clear the vector store"""
		self.client.delete_collection(self.collection_name)
		self.collection = self.client.create_collection(self.collection_name)
		print("✅ Vector store reset")


if __name__ == "__main__":
	# Import here to avoid circular dependency
	import sys
	sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
	
	from src.rag.document_loader import SAPDocumentLoader
	
	print("="*80)
	print("VECTOR STORE TEST")
	print("="*80)
	
	# Load documents
	loader = SAPDocumentLoader()
	chunks = loader.prepare_for_vectorstore()
	
	if not chunks:
		print("\n⚠️  No documents found. Add docs to docs/service_cloud/")
		exit(1)
	
	# Create vector store
	vector_store = SAPVectorStore()
	vector_store.reset()
	vector_store.add_documents(chunks)
	
	# Test searches
	print("\n" + "="*80)
	print("TESTING SEARCH")
	print("="*80)
	
	# Single domain
	print("\n1️⃣ Single domain search:")
	results = vector_store.search("ticket assignment", domain_filter="service_cloud", top_k=2)
	for r in results:
		print(f"  - {r['metadata']['domain']}: {r['content'][:80]}...")
	
	# Multi-domain (THE FIX!)
	print("\n2️⃣ Multi-domain search (Service Cloud + CPI):")
	results = vector_store.search_multi_domain(
		"Service Cloud CPI integration",
		domains=["service_cloud", "cpi"],
		top_k_per_domain=2
	)
	for r in results:
		print(f"  - {r['metadata']['domain']}: {r['content'][:80]}...")