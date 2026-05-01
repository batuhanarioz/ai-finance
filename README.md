# FinAgent: Autonomous Multi-Agent Banking Framework 🏦🤖

[![Architecture: LangGraph](https://img.shields.io/badge/Architecture-LangGraph-red)](https://github.com/langchain-ai/langgraph)
[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Database: pgvector](https://img.shields.io/badge/Database-pgvector-blue)](https://github.com/pgvector/pgvector)
[![Evaluation: RAGAS](https://img.shields.io/badge/Evaluation-RAGAS-orange)](https://github.com/explodinggradients/ragas)

**FinAgent** is a production-grade, autonomous multi-agent system designed for secure financial operations. It leverages **LangGraph** for sophisticated agent orchestration, providing a transparent, secure, and observable AI banking experience.

## 🌟 Key Features

- **Autonomous Agent Orchestration**: Uses a Supervisor-Agent pattern to route requests between specialized agents (Banker, Risk Officer, Product Expert).
- **Modular Semantic Search**: High-performance RAG pipeline with `pgvector` hybrid search and ingestion indexing.
- **Enterprise Security**: 
  - **PII Data Masking**: Automatically redacts sensitive information.
  - **Security Auditing**: Real-time logging of every AI action.
  - **Guardrails**: Protection against SQLi, XSS, and unauthorized transactions.
- **Observability Hub**: 
  - **Real-time Thought Diaries**: Watch the AI "think" through every node transition.
  - **Prometheus/Grafana Integration**: Monitor latency, request counts, and system health.
- **Data-Driven Evaluation**: Integrated **RAGAS** suite for measuring faithfulness, relevance, and precision.

## 🏗️ Architecture

```mermaid
graph TD
    User((User)) --> Frontend[Next.js Dashboard]
    Frontend --> API[FastAPI Orchestrator]
    API --> Supervisor{Supervisor Agent}
    Supervisor --> Banker[Transactional Agent]
    Supervisor --> Risk[Risk Officer]
    Supervisor --> Product[Product Expert]
    Banker --> CoreBank[Bank MCP Server]
    Product --> RAG[RAG Engine + pgvector]
    API --> Security[Security Guardrails]
    API --> Monitoring[Prometheus/Grafana]
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API Key (added to `backend/.env`)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/finagent.git
   cd finagent
   ```
2. Setup environment variables:
   - Create `backend/.env` with your `OPENAI_API_KEY`.
3. Run with Docker Compose:
   ```bash
   docker compose up --build
   ```
4. Access the apps:
   - **Frontend**: `http://localhost:3000`
   - **API Metrics**: `http://localhost:8000/metrics`
   - **Grafana Dashboard**: `http://localhost:3001`

## 🎓 Interview & Architecture Deep Dive

This section serves as a study guide for understanding the "Senior" decisions made in this project.

### 1. Why LangGraph instead of simple LangChain?
- **State Management**: Simple chains are stateless. LangGraph allows for a persistent `AgentState`, enabling agents to "remember" previous steps in a complex workflow.
- **Cycles & Loops**: Real-world banking requires retries and corrections (e.g., if the Risk Officer rejects a transaction, we loop back to the user or banker). LangGraph handles these cyclic graphs natively.
- **Supervisor Pattern**: Instead of one giant prompt, we use a "Router" (Supervisor) to delegate tasks. This reduces "LLM distraction" and improves tool-calling accuracy.

### 2. The RAGAS Evaluation Strategy
- **Faithfulness**: Measures if the answer is derived *solely* from the retrieved context. (Crucial for preventing hallucinations in banking).
- **Answer Relevance**: Ensures the AI actually addresses the user's query rather than giving generic info.
- **Context Precision**: Evaluates if the most relevant information is at the top of the search results (optimizing `pgvector` performance).

### 3. Observability & Monitoring (The "SRE" Side)
- **Prometheus**: Tracks system-level metrics like `request_latency_seconds`. In an interview, you can explain how this helps monitor the "cost vs speed" trade-off of different LLM models.
- **Grafana**: Provides the visual proof of system health, crucial for enterprise stakeholders.
- **Thought Diaries**: This isn't just a UI feature; it's a "Traceability" requirement. It shows exactly which agent made which decision at what time.

### 4. Enterprise Security Guardrails
- **PII Masking**: We use regex-based and LLM-based masking to ensure data like IBANs or Phone Numbers don't leak into the model's training logs or third-party providers.
- **Prompt Injection Defense**: By using a structured `BaseModel` for chat requests and a Supervisor node, we limit the user's ability to "break" the agent logic.

## 📊 Evaluation (RAGAS)
Run the evaluation suite to measure system performance:
```bash
docker exec -it fin-agent-backend python backend/eval/evaluator.py
```

## 🛡️ Security Audit
Every transaction and AI response is logged in `backend/data/audit_logs.jsonl` for compliance and auditing.

---
Built with ❤️ for the future of Autonomous Finance.
