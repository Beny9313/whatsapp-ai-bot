"""
Agent state definition.
Tracks what the agent knows at each step of the reasoning loop.
"""

from typing import TypedDict, List, Optional
from pydantic import BaseModel

class AgentState(TypedDict):
    """
    State that flows through the LangGraph agent.
    Each node reads from and writes to this state.
    """
    
    # Input
    query: str                          # User's question
    user_id: str                        # WhatsApp number (for memory later)
    
    # Classification
    primary_domain: Optional[str]       # service_cloud, fsm, etc.
    secondary_domains: List[str]        # For cross-domain queries
    is_cross_domain: bool              # True if multiple domains involved
    
    # Planning
    plan: Optional[str]                # Step-by-step plan
    
    # Retrieval (Day 3 - mock for now)
    retrieved_docs: List[str]          # Relevant documentation
    
    # Generation
    answer: Optional[str]              # Final response to user
    
    # Metadata
    confidence: float                  # Classification confidence
    error: Optional[str]               # Error message if something fails


class ClassificationResult(BaseModel):
    """Structured output from domain classifier"""
    primary_domain: str
    secondary_domains: List[str] = []
    is_cross_domain: bool = False
    confidence: float
    reasoning: str  