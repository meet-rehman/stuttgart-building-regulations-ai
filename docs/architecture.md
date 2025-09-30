# System Architecture

## Multi-Agent Orchestration

This system uses CrewAI to orchestrate 5 specialized agents that work sequentially and can delegate tasks to each other for comprehensive building regulation analysis.

## Agent Flow

### Sequential Processing
1. **User Query** → System receives building regulation question
2. **Document Research Specialist** → Searches 8,826+ documents using semantic vector search
3. **Regulatory Legal Analyst** → Interprets legal hierarchy (Federal > State > Local)
4. **Technical Standards Expert** → Analyzes DIN standards and technical requirements
5. **Compliance Strategy Advisor** → Develops cost-benefit analysis and timelines
6. **Professional Synthesis Manager** → Creates final consultation report

### Intelligent Delegation
Agents can delegate sub-tasks to specialists:
- Research Specialist asks Legal Analyst for hierarchy clarification
- Legal Analyst consults Technical Expert for DIN standard details
- Strategy Advisor requests Synthesis Manager for report formatting

## Data Processing Pipeline

### Document Processing
- **Input:** 9 PDF documents containing German building regulations
- **Processing:** Text extraction, chunking, metadata enrichment
- **Output:** 8,826 processed document chunks with embeddings

### Vector Search
- **Model:** SentenceTransformers (all-MiniLM-L6-v2)
- **Embedding Dimension:** 384
- **Search Method:** Semantic similarity using cosine distance
- **Storage:** Precomputed embeddings for fast retrieval

### RAG (Retrieval-Augmented Generation)
1. User query is embedded using SentenceTransformers
2. Semantic search finds top-k relevant document chunks
3. Retrieved context is provided to LLM (GPT-4 via Groq)
4. LLM generates response grounded in retrieved documents

## Deployment Architecture

### Railway Platform
- Docker containerization for consistent deployment
- Automated health checks every 5 minutes
- Environment variable management for API keys
- Automatic restarts on failure

### API Layer
- FastAPI framework with async support
- Uvicorn ASGI server
- CORS enabled for web access
- Comprehensive error handling

### Monitoring
- `/health` endpoint reports system status
- Agent readiness checks
- Document count verification
- API key validation