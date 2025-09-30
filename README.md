# stuttgart-building-regulations-ai
Multi-agent AI system for German building regulation analysis - 5 specialized agents processing 8,826+ documents


[![Live Demo](https://img.shields.io/badge/Live-Demo-blue)](https://stuttgartregagent-production.up.railway.app/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

### Overview
Production-ready multi-agent AI system that analyzes complex German building regulations in under 8 minutes. Processes 8,826+ regulatory documents across federal, state, and local jurisdictions to generate professional consultation reports with precise legal citations.

### 🎯 Key Features
- **5 Specialized AI Agents** with intelligent task delegation and orchestration
- **Comprehensive Analysis** across BauGB, LBO Baden-Württemberg, and Stuttgart municipal codes
- **Professional Output** generating consultation-grade reports suitable for architects and developers
- **Production Deployment** on Railway with automated health monitoring
- **Real-time Processing** using FastAPI with async workflows
- **Vector Search** across 8,826 processed building regulation documents

### 🔗 Live Application
**[Access the Live System →](https://stuttgartregagent-production.up.railway.app/)**

**API Documentation:** [Swagger UI](https://stuttgartregagent-production.up.railway.app/docs)

### 🏗️ Architecture Overview

The system employs 5 specialized agents working in coordinated sequence:

1. **Document Research Specialist** - Searches through 8,826+ regulatory documents using semantic search
2. **Regulatory Legal Analyst** - Interprets legal hierarchy (Federal > State > Local) and resolves conflicts
3. **Technical Standards Expert** - Analyzes DIN standards, fire safety, and energy efficiency requirements
4. **Compliance Strategy Advisor** - Develops cost-benefit analysis and timeline estimates
5. **Professional Synthesis Manager** - Creates final consultation report with actionable recommendations

**Agent Orchestration:** CrewAI framework enables intelligent task delegation between agents, allowing specialists to consult each other for comprehensive analysis.

### 💬 Sample Query & Response

**Input:**
```json
{
  "query": "I have an 800m² lot in Stuttgart-Mitte zoned as WA (general residential area). What's the maximum building coverage ratio and how many stories can I build?"
}
Output Highlights:

Maximum building coverage ratio: 0.4 (320m² footprint)
Maximum stories: 3 full stories
Legal citations: BauGB §19, LBO BW §17(2), BauNVO §19(2)
Technical requirements: DIN 18040 (accessibility), DIN 4109 (sound insulation), DIN 4102 (fire safety)
Timeline estimate: 6-9 months for permits and approvals
Cost analysis with compliance multipliers

🛠️ Technical Stack
Backend Framework:

FastAPI 0.104.1
Python 3.11
Uvicorn ASGI server

AI/ML Components:

CrewAI for multi-agent orchestration
OpenAI GPT-4 API
SentenceTransformers (all-MiniLM-L6-v2)
Vector embeddings for semantic search

Data Processing:

8,826 processed German building regulation documents
Precomputed embeddings for fast retrieval
RAG (Retrieval-Augmented Generation) pipeline

Deployment:

Railway platform with Docker containerization
Automated health checks
Environment-based configuration
99%+ uptime

🚀 Quick Start
bash# Clone repository
git clone https://github.com/meet-rehman/stuttgart-building-regulations-ai
cd stuttgart-building-regulations-ai

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key-here"

# Run application
uvicorn multi_agent_app:app --reload --port 8000
Visit http://localhost:8000 for the interface or http://localhost:8000/docs for API documentation.
📡 API Endpoints
EndpointMethodDescription/GETMain web interface/multi-agentPOSTMulti-agent analysis endpoint/chatPOSTLegacy single-agent endpoint/healthGETSystem health and agent status/docsGETInteractive API documentation
📊 Performance Metrics

Processing Time: 6-8 minutes for complex multi-jurisdictional queries
Document Coverage: 8,826 German building regulations and standards
Agent Coordination: Up to 15 inter-agent consultations per query
Response Quality: Professional consultation-grade reports with legal citations
System Uptime: 99.5% on Railway production deployment

🎯 Use Cases
This system is designed for:

Architects - Preliminary regulatory research and site assessment
Real Estate Developers - Feasibility analysis and compliance planning
Urban Planners - Multi-jurisdictional regulation analysis
Legal Consultants - Building code research and citation verification

📁 Project Structure
stuttgart-building-regulations-ai/
├── multi_agent_app.py        # Main FastAPI application
├── crew_ai_system.py          # Multi-agent orchestration logic
├── precomputed_rag.py         # RAG system with vector search
├── schemas.py                 # Pydantic data models
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── config/                    # Agent and task configurations
├── tools/                     # Custom tools for agents
├── static/                    # Frontend assets
└── embeddings/                # Precomputed vector embeddings
🔍 System Status
🟢 Production Ready - Live at stuttgartregagent-production.up.railway.app
The system is actively processing real-world building regulation queries with validated accuracy against Stuttgart Bauamt requirements.
⚖️ Legal Disclaimer
This system provides preliminary regulatory research and should not replace professional legal or architectural consultation. All outputs should be verified with licensed professionals and local building authorities (Bauamt) before making project decisions.
📧 Contact
For technical inquiries, collaboration opportunities, or commercial discussions:

GitHub: meet-rehman
Project Issues: GitHub Issues

📄 License
MIT License - See LICENSE file for details.

Built with: CrewAI • FastAPI • OpenAI • Railway • Python
'''
