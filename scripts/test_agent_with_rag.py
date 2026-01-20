"""
Test agent with real RAG retrieval.
DAY 3: Now uses 46,682 real SAP docs!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.sap_agent import run_agent

def test_agent_rag(query: str):
    """Test agent with real documentation"""
    
    print(f"\n{'='*80}")
    print(f"QUERY: {query}")
    print(f"{'='*80}\n")
    
    result = run_agent(query)
    
    print(f"\n📊 RESULTS:")
    print(f"  Domain: {result['primary_domain']}")
    print(f"  Cross-domain: {result['is_cross_domain']}")
    if result['is_cross_domain']:
        print(f"  Secondary domains: {result['secondary_domains']}")
    print(f"  Docs retrieved: {len(result['retrieved_docs'])}")
    
    print(f"\n💬 ANSWER:")
    print(result['answer'])
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    print("="*80)
    print("AGENT WITH REAL RAG - DAY 3")
    print("="*80)
    
    # Test cases
    test_queries = [
        # Single domain
        "How do I configure automated ticket assignment in Service Cloud?",
        
        # Cross-domain (THE BIG TEST!)
        "How does Service Cloud integrate with CPI for ticket data export?",
        
        # Another domain
        "What are the CPQ quote template configuration options?",
        
        # FSM
        "How do I set up work order scheduling in FSM?"
    ]
    
    for query in test_queries:
        test_agent_rag(query)