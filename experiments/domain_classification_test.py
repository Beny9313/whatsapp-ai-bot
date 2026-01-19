"""
Test domain classification accuracy using Groq.
"""

import os
from dotenv import load_dotenv
from groq import Groq
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")

TEST_CASES = [
    {
        "query": "How do I configure automated ticket assignment in Service Cloud?",
        "expected": {"primary": "service_cloud", "cross_domain": False}
    },
    {
        "query": "How do FSM work orders sync with Service Cloud tickets?",
        "expected": {"primary": "fsm", "secondary": ["service_cloud"], "cross_domain": True}
    },
    {
        "query": "Configure OAuth for CPI integration with Sales Cloud",
        "expected": {"primary": "cpi", "secondary": ["sales_cloud"], "cross_domain": True}
    },
    {
        "query": "CPQ quote approval workflow setup",
        "expected": {"primary": "cpq", "cross_domain": False}
    },
    {
        "query": "How does opportunity data from Sales Cloud flow through CPI to create service tickets?",
        "expected": {"primary": "sales_cloud", "secondary": ["cpi", "service_cloud"], "cross_domain": True}
    }
]

def classify_domain(query: str) -> dict:
    """
    Core classification function for your agent.
    Must be highly accurate (>90%).
    """
    
    system_prompt = """You are a domain classification expert for SAP CX systems.

Available domains:
- service_cloud: Customer service, tickets, cases, support workflows
- fsm: Field service management, work orders, scheduling, technicians  
- sales_cloud: Opportunities, leads, accounts, sales processes
- cpq: Configure-Price-Quote, product configuration, pricing rules
- cpi: Cloud Platform Integration, data flows, API integration, middleware

Classify user queries into these domains.

Output ONLY valid JSON with this structure:
{
  "primary_domain": "most relevant domain",
  "secondary_domains": ["other involved domains"],
  "is_cross_domain": true/false,
  "confidence": 0.95,
  "reasoning": "brief explanation"
}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Classify this query: {query}"}
        ],
        temperature=0.1,
        max_tokens=512,
        response_format={"type": "json_object"}
    )
    
    response_text = response.choices[0].message.content
    return json.loads(response_text)

def test_classification():
    """Run all test cases and report accuracy"""
    
    results = []
    correct = 0
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test['query']}")
        print(f"{'='*80}")
        
        try:
            classification = classify_domain(test['query'])
            
            # Check correctness
            is_correct = (
                classification['primary_domain'] == test['expected']['primary'] and
                classification['is_cross_domain'] == test['expected']['cross_domain']
            )
            
            if is_correct:
                correct += 1
                print("✅ CORRECT")
            else:
                print("❌ INCORRECT")
            
            print(f"\nExpected: {test['expected']}")
            print(f"Got: {classification}")
            
            results.append({
                "query": test['query'],
                "expected": test['expected'],
                "actual": classification,
                "correct": is_correct
            })
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "query": test['query'],
                "expected": test['expected'],
                "actual": None,
                "correct": False,
                "error": str(e)
            })
    
    accuracy = (correct / len(TEST_CASES)) * 100
    print(f"\n{'='*80}")
    print(f"ACCURACY: {accuracy:.1f}% ({correct}/{len(TEST_CASES)})")
    print(f"{'='*80}")
    
    return results, accuracy

if __name__ == "__main__":
    print(f"🤖 Using Groq: {MODEL}\n")
    results, accuracy = test_classification()
    
    if accuracy < 90:
        print("\n⚠️  Classification accuracy below 90%.")
        print("Action: Refine the system prompt in classify_domain()")
    else:
        print("\n🎉 Classification ready for production!")