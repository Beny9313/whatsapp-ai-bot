"""
Demonstrates agent reasoning using Groq API (Free + Fast).
Shows difference between simple RAG vs agent with planning.
"""

import os
from dotenv import load_dotenv
from groq import Groq
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Model selection (Groq models)
MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")

# Simulated SAP documentation
MOCK_DOCS = {
    "service_cloud": [
        "Service ticket configuration: Navigate to Admin > Service > Ticket Types. Configure workflow rules under Automation > Workflows.",
        "Service ticket routing: Set up assignment rules in Admin > Service > Assignment Rules. Configure based on category, priority, or custom fields.",
        "Integration with CPI: Service Cloud can send ticket data to CPI via OData APIs. Configure in Admin > Integration > API Settings."
    ],
    "cpi": [
        "CPI authentication: Configure OAuth 2.0 in Integration Suite. Generate client credentials in Security settings.",
        "CPI integration flows: Create iFlow in Design workspace. Configure sender/receiver adapters based on source system."
    ]
}

def simple_rag(question: str) -> str:
    """Approach 1: Simple RAG - just retrieve and answer"""
    all_docs = [doc for docs in MOCK_DOCS.values() for doc in docs]
    context = "\n".join(all_docs[:2])
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer using only the provided context."
        }],
        temperature=0.3,
        max_tokens=1024
    )
    
    return response.choices[0].message.content

def agent_with_reasoning(question: str) -> dict:
    """Approach 2: Agent - classify domain, plan, retrieve, reason"""
    
    # STEP 1: Domain Classification
    classification_response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": f"""Classify this SAP CX question into domains.

Available domains: service_cloud, fsm, sales_cloud, cpq, cpi

Question: {question}

Respond ONLY with valid JSON in this exact format (no markdown, no explanation):
{{
  "primary_domain": "...",
  "secondary_domains": [],
  "is_cross_domain": false
}}"""
        }],
        temperature=0.1,
        max_tokens=256,
        response_format={"type": "json_object"}
    )
    
    classification_text = classification_response.choices[0].message.content
    classification = json.loads(classification_text)
    print(f"\n🔍 CLASSIFICATION: {classification}")
    
    # STEP 2: Planning
    planning_response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": f"""Question: {question}
Domains involved: {json.dumps(classification)}

Create a step-by-step plan to answer this question.
Consider:
1. What information is needed from each domain?
2. In what order should we retrieve it?
3. Are there dependencies between domains?

Output your plan as numbered steps."""
        }],
        temperature=0.3,
        max_tokens=1024
    )
    
    plan = planning_response.choices[0].message.content
    print(f"\n📋 PLAN:\n{plan}")
    
    # STEP 3: Domain-Filtered Retrieval
    primary_domain = classification["primary_domain"]
    relevant_docs = MOCK_DOCS.get(primary_domain, [])
    
    if classification.get("is_cross_domain"):
        for domain in classification.get("secondary_domains", []):
            relevant_docs.extend(MOCK_DOCS.get(domain, []))
    
    context = "\n\n".join(relevant_docs)
    print(f"\n📚 RETRIEVED {len(relevant_docs)} docs from: {primary_domain}" + 
          (f" + {classification.get('secondary_domains')}" if classification.get("is_cross_domain") else ""))
    
    # STEP 4: Reasoning & Answer
    final_response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": f"""Question: {question}

Plan: {plan}

Context from {primary_domain}:
{context}

Using the plan and context, provide a comprehensive answer. 
If the question requires information from multiple domains, explain how they connect."""
        }],
        temperature=0.3,
        max_tokens=2048
    )
    
    return {
        "classification": classification,
        "plan": plan,
        "docs_retrieved": len(relevant_docs),
        "answer": final_response.choices[0].message.content
    }

if __name__ == "__main__":
    print(f"🤖 Using Groq: {MODEL}\n")
    
    questions = [
        "How do I configure service ticket routing in Service Cloud?",
        "How do I integrate Service Cloud tickets with CPI for downstream processing?"
    ]
    
    for q in questions:
        print("\n" + "="*80)
        print(f"QUESTION: {q}")
        print("="*80)
        
        print("\n--- APPROACH 1: Simple RAG ---")
        try:
            simple_answer = simple_rag(q)
            print(simple_answer)
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n--- APPROACH 2: Agent with Reasoning ---")
        try:
            agent_result = agent_with_reasoning(q)
            print(f"\n✅ FINAL ANSWER:\n{agent_result['answer']}")
            print(f"\n📊 STATS: {agent_result['docs_retrieved']} docs from {agent_result['classification']['primary_domain']}")
        except Exception as e:
            print(f"Error: {e}")