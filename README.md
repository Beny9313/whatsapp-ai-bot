# SAP CX WhatsApp AI Agent

A production-grade AI agent that helps SAP C4C consultants with documentation queries via WhatsApp.

## Architecture

**Agent Type:** Hybrid (Single agent with domain-aware RAG)

**Domains Supported:**
1. Service Cloud
2. Field Service Management (FSM)
3. Sales Cloud
4. CPQ (Configure-Price-Quote)
5. Cloud Platform Integration (CPI)

**Key Features:**
- Domain classification (routes queries to relevant documentation)
- Multi-domain support (handles cross-domain questions)
- LangGraph orchestration (reasoning loops)
- WhatsApp integration via Twilio

## Project Status

- [x] Day 0: Architecture experiments
- [ ] Day 1-2: Webhook setup
- [ ] Day 3: WhatsApp integration
- [ ] Day 4-5: LangGraph agent
- [ ] Day 6: RAG with Service Cloud docs
- [ ] Day 7: Deployment

## Setup
```bash
# 1. Clone repo
git clone https://github.com/Beny9313/whatsapp-ai-bot.git
cd whatsapp-ai-bot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# 5. Run Day 0 experiments
python experiments/why_agents_matter.py
python experiments/domain_classification_test.py
```

## Directory Structure
```
whatsapp-sap-agent/
├── docs/                    # SAP documentation by domain
│   ├── service_cloud/
│   ├── fsm/
│   ├── sales_cloud/
│   ├── cpq/
│   └── cpi/
├── experiments/             # Day 0: Understanding agents
│   ├── why_agents_matter.py
│   └── domain_classification_test.py
├── src/
│   ├── agents/             # Agent logic (Day 4-5)
│   ├── tools/              # Agent tools (Day 4-5)
│   └── rag/                # Vector store & retrieval (Day 6)
└── tests/                  # Test suite
```

## Learning Path

This project follows Option 3 (Hybrid Architecture):
- Single agent with domain classification
- Domain-filtered RAG retrieval
- Handles both single-domain and cross-domain queries
- Scalable to multi-agent system later

## Resources

- [Original Tutorial](https://github.com/neural-maze/ava-whatsapp-agent-course)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Claude API Docs](https://docs.anthropic.com/)
