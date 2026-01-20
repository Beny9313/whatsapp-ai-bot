"""
Load SAP documentation (PDF, MD, TXT) and prepare for vector storage.
Supports multiple domains with metadata tagging.
"""

import os
from pathlib import Path
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class SAPDocumentLoader:
	"""
	Loads SAP CX documentation from domain-specific folders.
	Supports: .pdf, .md, .txt
	Tags each chunk with domain metadata for filtered retrieval.
	"""
	
	def __init__(self, docs_base_path: str = "docs"):
		self.docs_base_path = Path(docs_base_path)
		self.domains = ["service_cloud", "fsm", "sales_cloud", "cpq", "cpi"]
		
		# Text splitter for chunking
		self.text_splitter = RecursiveCharacterTextSplitter(
			chunk_size=1000,
			chunk_overlap=200,
			length_function=len,
			separators=["\n\n", "\n", ". ", " ", ""]
		)
	
	def load_domain_docs(self, domain: str) -> List[Document]:
		"""Load all documents for a specific domain (PDF, MD, TXT)"""
		
		domain_path = self.docs_base_path / domain
		
		if not domain_path.exists():
			print(f"⚠️  {domain_path} does not exist, creating...")
			domain_path.mkdir(parents=True, exist_ok=True)
			return []
		
		documents = []
		
		# Load PDFs
		pdf_files = list(domain_path.glob("**/*.pdf"))
		for pdf_file in pdf_files:
			try:
				loader = PyPDFLoader(str(pdf_file))
				pdf_docs = loader.load()
				
				for doc in pdf_docs:
					doc.metadata["domain"] = domain
					doc.metadata["source_file"] = pdf_file.name
					doc.metadata["file_type"] = "pdf"
				
				documents.extend(pdf_docs)
				print(f"  ✅ PDF: {pdf_file.name} ({len(pdf_docs)} pages)")
				
			except Exception as e:
				print(f"  ❌ Error loading {pdf_file.name}: {e}")
		
		# Load Markdown files
		md_files = list(domain_path.glob("**/*.md"))
		for md_file in md_files:
			try:
				with open(md_file, 'r', encoding='utf-8') as f:
					content = f.read()
				
				doc = Document(
					page_content=content,
					metadata={
						"domain": domain,
						"source_file": md_file.name,
						"file_type": "markdown"
					}
				)
				documents.append(doc)
				print(f"  ✅ MD: {md_file.name}")
				
			except Exception as e:
				print(f"  ❌ Error loading {md_file.name}: {e}")
		
		# Load Text files
		txt_files = list(domain_path.glob("**/*.txt"))
		for txt_file in txt_files:
			try:
				with open(txt_file, 'r', encoding='utf-8') as f:
					content = f.read()
				
				doc = Document(
					page_content=content,
					metadata={
						"domain": domain,
						"source_file": txt_file.name,
						"file_type": "text"
					}
				)
				documents.append(doc)
				print(f"  ✅ TXT: {txt_file.name}")
				
			except Exception as e:
				print(f"  ❌ Error loading {txt_file.name}: {e}")
		
		if documents:
			pages = len(documents)
			print(f"✅ {domain}: {pages} pages loaded")
		
		return documents
	
	def load_all_docs(self) -> Dict[str, List[Document]]:
		"""Load documents from all domains"""
		
		all_docs = {}
		
		for domain in self.domains:
			print(f"\n📂 {domain}...")
			docs = self.load_domain_docs(domain)
			if docs:
				all_docs[domain] = docs
		
		total_pages = sum(len(docs) for docs in all_docs.values())
		print(f"\n📚 TOTAL: {total_pages} pages across {len(all_docs)} domains")
		
		return all_docs
	
	def chunk_documents(self, documents: List[Document]) -> List[Document]:
		"""Split documents into chunks for embedding"""
		
		chunks = self.text_splitter.split_documents(documents)
		print(f"✂️  {len(chunks)} chunks created")
		
		return chunks
	
	def prepare_for_vectorstore(self) -> List[Document]:
		"""Load all docs, chunk them, prepare for vector storage"""
		
		print("="*80)
		print("📖 LOADING SAP CX DOCUMENTATION")
		print("="*80)
		
		all_docs = self.load_all_docs()
		
		# Flatten
		all_documents = []
		for domain, docs in all_docs.items():
			all_documents.extend(docs)
		
		if not all_documents:
			print("\n⚠️  No documents found!")
			return []
		
		# Chunk
		chunks = self.chunk_documents(all_documents)
		
		# Stats
		from collections import Counter
		domain_counts = Counter(chunk.metadata.get('domain') for chunk in chunks)
		file_type_counts = Counter(chunk.metadata.get('file_type') for chunk in chunks)
		
		print(f"\n📊 BY DOMAIN:")
		for domain, count in domain_counts.items():
			print(f"  {domain}: {count} chunks")
		
		print(f"\n📊 BY FILE TYPE:")
		for file_type, count in file_type_counts.items():
			print(f"  {file_type}: {count} chunks")
		
		return chunks


if __name__ == "__main__":
	loader = SAPDocumentLoader()
	chunks = loader.prepare_for_vectorstore()
	
	if chunks:
		print(f"\n✅ READY: {len(chunks)} chunks for vector store")
	else:
		print("\n⚠️  Add documents to docs/ folders first")