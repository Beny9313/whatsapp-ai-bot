"""
Agent nodes (functions that process each state).
Each node is a step in the reasoning loop.
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq

# Handle both direct execution and module import
try:
	from .state import AgentState, ClassificationResult
except ImportError:
	from state import AgentState, ClassificationResult

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")

# Domain definitions (reused from Day 0)
DOMAIN_DESCRIPTIONS = """
Available domains:
- service_cloud: Customer service, tickets, cases, support workflows
- fsm: Field service management, work orders, scheduling, technicians  
- sales_cloud: Opportunities, leads, accounts, sales processes
- cpq: Configure-Price-Quote, product configuration, pricing rules
- cpi: Cloud Platform Integration, data flows, API integration, middleware
"""


def classify_node(state: AgentState) -> AgentState:
	"""
	Node 1: Classify the query into SAP domains.
	This is your Day 0 classification code, wrapped as a LangGraph node.
	"""
	
	query = state["query"]
	
	try:
		response = client.chat.completions.create(
			model=MODEL,
			messages=[
				{
					"role": "system",
					"content": f"""You are a domain classification expert for SAP CX systems.

{DOMAIN_DESCRIPTIONS}

Output ONLY valid JSON with this structure:
{{
  "primary_domain": "most relevant domain",
  "secondary_domains": ["other involved domains"],
  "is_cross_domain": true/false,
  "confidence": 0.95,
  "reasoning": "brief explanation"
}}"""
				},
				{"role": "user", "content": f"Classify this query: {query}"}
			],
			temperature=0.1,
			max_tokens=512,
			response_format={"type": "json_object"}
		)
		
		result = json.loads(response.choices[0].message.content)
		
		# Update state with classification
		state["primary_domain"] = result["primary_domain"]
		state["secondary_domains"] = result.get("secondary_domains", [])
		state["is_cross_domain"] = result.get("is_cross_domain", False)
		state["confidence"] = result.get("confidence", 0.0)
		
		print(f"✅ Classification: {result['primary_domain']} (confidence: {result['confidence']})")
		
	except Exception as e:
		state["error"] = f"Classification failed: {str(e)}"
		print(f"❌ Classification error: {e}")
	
	return state


def plan_node(state: AgentState) -> AgentState:
	"""
	Node 2: Create a step-by-step plan to answer the query.
	"""
	
	query = state["query"]
	primary_domain = state.get("primary_domain", "unknown")
	is_cross_domain = state.get("is_cross_domain", False)
	
	try:
		response = client.chat.completions.create(
			model=MODEL,
			messages=[{
				"role": "user",
				"content": f"""Question: {query}
Primary domain: {primary_domain}
Cross-domain: {is_cross_domain}

Create a brief step-by-step plan to answer this SAP CX question.
Consider:
1. What information is needed?
2. What order should we retrieve it?
3. Are there dependencies between domains?

Output 3-5 numbered steps."""
			}],
			temperature=0.3,
			max_tokens=512
		)
		
		plan = response.choices[0].message.content
		state["plan"] = plan
		
		print(f"✅ Plan created:\n{plan[:100]}...")
		
	except Exception as e:
		state["error"] = f"Planning failed: {str(e)}"
		print(f"❌ Planning error: {e}")
	
	return state


def retrieve_node(state: AgentState) -> AgentState:
	"""
	Node 3: Retrieve relevant documentation using RAG.
	DAY 3: Real vector search with multi-domain support!
	"""
	
	primary_domain = state.get("primary_domain", "unknown")
	is_cross_domain = state.get("is_cross_domain", False)
	secondary_domains = state.get("secondary_domains", [])
	query = state.get("query", "")
	
	try:
		# Import vector store
		import sys
		import os
		sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
		from src.rag.vector_store import SAPVectorStore
		
		# Initialize vector store
		vector_store = SAPVectorStore()
		
		if is_cross_domain and secondary_domains:
			# MULTI-DOMAIN RETRIEVAL (THE FIX!)
			domains = [primary_domain] + secondary_domains
			print(f"🔍 Multi-domain retrieval: {domains}")
			
			results = vector_store.search_multi_domain(
				query=query,
				domains=domains,
				top_k_per_domain=3
			)
		else:
			# SINGLE-DOMAIN RETRIEVAL
			print(f"🔍 Single-domain retrieval: {primary_domain}")
			
			results = vector_store.search(
				query=query,
				domain_filter=primary_domain,
				top_k=5
			)
		
		# Extract content
		docs = [r['content'] for r in results]
		state["retrieved_docs"] = docs
		
		print(f"✅ Retrieved {len(docs)} docs")
		
	except Exception as e:
		print(f"❌ Retrieval error: {e}")
		state["retrieved_docs"] = [
			f"Error retrieving documentation. Using general knowledge about {primary_domain}."
		]
	
	return state


def generate_node(state: AgentState) -> AgentState:
	"""
	Node 4: Generate final answer using plan and retrieved docs.
	"""
	
	query = state["query"]
	plan = state.get("plan", "No plan available")
	docs = state.get("retrieved_docs", [])
	primary_domain = state.get("primary_domain", "unknown")
	
	try:
		context = "\n\n".join(docs)
		
		response = client.chat.completions.create(
			model=MODEL,
			messages=[{
				"role": "user",
				"content": f"""You are an SAP CX expert. Answer using ONLY the provided documentation.

	Question: {query}

	Documentation:
	{context}

	Instructions:
	- Answer directly and concisely
	- Use 3-5 bullet points for steps
	- Include specific technical details from docs
	- Format for WhatsApp (professional, minimal emojis)
	- DO NOT repeat yourself
	- If docs are unclear, acknowledge it
	- Keep under 400 words

	Answer:"""
			}],
			temperature=0.2,
			max_tokens=600
		)
		
		answer = response.choices[0].message.content
		state["answer"] = answer
		
		print(f"✅ Answer generated ({len(answer)} chars)")
		
	except Exception as e:
		state["error"] = f"Generation failed: {str(e)}"
		state["answer"] = "Sorry, I encountered an error generating the answer."
		print(f"❌ Generation error: {e}")
	
	return state