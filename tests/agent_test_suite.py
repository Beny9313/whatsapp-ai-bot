"""
Test suite for SAP CX agent.
Run before deploying updates.
"""

test_cases = [
    # Single domain - Service Cloud
    {
        "query": "How do I configure ticket assignment?",
        "expected_domain": "service_cloud",
        "expected_cross_domain": False
    },
    # Single domain - FSM
    {
        "query": "How do I schedule work orders in FSM?",
        "expected_domain": "fsm",
        "expected_cross_domain": False
    },
    # Cross-domain - Service Cloud + CPI
    {
        "query": "How does Service Cloud integrate with CPI?",
        "expected_domain": "service_cloud",
        "expected_cross_domain": True,
        "expected_secondary": ["cpi"]
    },
    # CPQ
    {
        "query": "How do I configure quote templates?",
        "expected_domain": "cpq",
        "expected_cross_domain": False
    },
    # Sales Cloud
    {
        "query": "How do I set up opportunity workflows?",
        "expected_domain": "sales_cloud",
        "expected_cross_domain": False
    }
]
# Run: python tests/agent_test_suite.py