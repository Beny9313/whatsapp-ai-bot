"""
LangGraph agent for SAP CX queries.
Orchestrates: classify → plan → retrieve → generate
"""

from langgraph.graph import StateGraph, END

# Handle both direct execution and module import
try:
    from .state import AgentState
    from .nodes import classify_node, plan_node, retrieve_node, generate_node
except ImportError:
    from state import AgentState
    from nodes import classify_node, plan_node, retrieve_node, generate_node


def create_sap_agent():
    """
    Create the SAP CX agent graph.
    
    Flow:
    START → classify → plan → retrieve → generate → END
    """
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classify", classify_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)
    
    # Define edges (flow)
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "plan")
    workflow.add_edge("plan", "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    
    # Compile
    agent = workflow.compile()
    
    return agent


def run_agent(query: str, user_id: str = "test_user") -> dict:
    """
    Run the agent on a query.
    
    Args:
        query: User's question
        user_id: User identifier (WhatsApp number)
    
    Returns:
        Final state with answer
    """
    
    # Initialize state
    initial_state = {
        "query": query,
        "user_id": user_id,
        "primary_domain": None,
        "secondary_domains": [],
        "is_cross_domain": False,
        "plan": None,
        "retrieved_docs": [],
        "answer": None,
        "confidence": 0.0,
        "error": None
    }
    
    # Create and run agent
    agent = create_sap_agent()
    final_state = agent.invoke(initial_state)
    
    return final_state


# Test function
if __name__ == "__main__":
    test_queries = [
        "How do I configure service ticket routing in Service Cloud?",
        "How do FSM work orders integrate with CPI?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print(f"{'='*80}\n")
        
        result = run_agent(query)
        
        print(f"\n📊 RESULTS:")
        print(f"Domain: {result['primary_domain']}")
        print(f"Confidence: {result['confidence']}")
        print(f"\n💬 ANSWER:\n{result['answer']}")