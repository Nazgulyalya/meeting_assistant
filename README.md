# 🎤 Meeting Assistant — Multi-Agent System

![Tests](https://img.shields.io/badge/tests-22%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-purple)
![LangGraph](https://img.shields.io/badge/orchestration-LangGraph-orange)
![RAG](https://img.shields.io/badge/RAG-ChromaDB-yellow)

> Multi-agent AI system that transforms meeting audio into structured insights, action items, and automated follow-ups. **Outperforms commercial tools** by adding cross-meeting memory and contradiction detection.


Multi-agent AI system that transforms meeting transcripts and audio into structured insights, action items, follow-up emails, and calendar events. Connects past meetings via RAG to provide institutional memory that commercial tools like Otter.ai and Fireflies lack.

## ✨ Features

- 🎙️ **Audio or text input** — Whisper-powered transcription, fully local
- 🧠 **Cross-meeting memory** — RAG retrieves relevant past decisions and flags contradictions
- ✅ **Action extraction** — tasks with owners, deadlines, priorities, and confidence scores
- 📊 **Participation analytics** — who spoke how much (inclusivity layer)
- 📧 **Gmail integration** — sends follow-up emails via MCP
- 📅 **Calendar integration** — schedules follow-ups via Google Calendar MCP
- 🔒 **PII anonymization** — emails, phones, SSN, cards, IPs scrubbed before storage
- 🔍 **LangSmith tracing** — full observability of all agent calls
- ⭐ **User feedback** — rating system built into UI

## 📸 Screenshots

![Main UI](docs/screenshots/01.png)
![Action Items](docs/screenshots/02.png)
![Memory Tab](docs/screenshots/03.png)
![Email Tab](docs/screenshots/04.png)
![Stats Tab](docs/screenshots/05.png)

## 🏗️ Architecture

```mermaid
flowchart LR
    Input[Audio/Text] --> TA[Transcript Agent]
    TA --> MA[Memory Agent<br/>RAG]
    MA --> AA[Action Agent]
    AA --> SA[Synthesis Agent]
    SA --> MCP[Gmail / Calendar MCP]
    
    DB[(ChromaDB<br/>30 meetings)] <--> MA
    
    style TA fill:#e1f5ff
    style MA fill:#fff4e1
    style AA fill:#e1ffe1
    style SA fill:#ffe1f5
```

Full diagrams: [docs/diagrams.md](docs/diagrams.md)

Audio/Text → Transcript Agent → Memory Agent (RAG) → Action Agent → Synthesis Agent → MCP (Gmail/Calendar)

Four agents orchestrated via LangGraph, each with distinct responsibilities. ChromaDB stores past meetings for semantic retrieval. All processing runs locally except LLM calls (Groq, free tier). 

## 📊 RAG Retrieval Quality

Measured on a hand-curated evaluation set of 10 queries with ground truth meeting IDs.

| Metric | Score |
|---|---|
| Precision@5 | 0.28 |
| Recall@5 | 1.0 |
| Mean Reciprocal Rank | 0.548 |

Run yourself: `python evals/rag_eval.py`

## 🚀 Quick Start

### 1. Clone and install
```bash
git clone <repo-url>
cd meeting-assistant
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API keys
Create `.env` in project root:
```env
GROQ_API_KEY=your_groq_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=meeting-assistant
```

Get keys:
- Groq: https://console.groq.com (free)
- LangSmith: https://smith.langchain.com (free tier)

### 3. Google API credentials (for MCP integrations)
1. Go to https://console.cloud.google.com
2. Enable Gmail API and Google Calendar API
3. Create OAuth Desktop credentials, download as `credentials.json` in project root

### 4. Seed the knowledge base
```bash
python data/seed_meetings.py
```

### 5. Run the app
```bash
streamlit run ui/app.py
```

Open http://localhost:8501

## 🧪 Testing

```bash
pytest tests/ -v
```

Includes positive cases (normal flows), negative cases (empty inputs), and adversarial cases (prompt injection).

## 📂 Project Structure 
meeting-assistant/
├── agents/              # 4 agents (transcript, memory, action, synthesis)
├── rag/                 # ChromaDB vectorstore, chunker, PII scrubber
├── mcp/                 # Gmail + Calendar MCP clients
├── orchestrator.py      # LangGraph multi-agent graph
├── ui/app.py            # Streamlit UI
├── tests/               # pytest suite
├── data/                # Seed meetings
├── utils/logger.py      # Audit trail logging
└── docs/                # Architecture Blueprint, Executive Summary, Self-Review

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM | Groq (llama-3.1-8b-instant) — free |
| Transcription | OpenAI Whisper (local) |
| Embeddings | sentence-transformers (local) |
| Vector DB | ChromaDB (local) |
| MCP | Gmail + Google Calendar APIs |
| Observability | LangSmith |
| UI | Streamlit |
| Tests | pytest |

## 📊 Why This Beats Commercial Tools

| Feature | Otter.ai | Fireflies | This System |
|---|---|---|---|
| Transcription | ✅ | ✅ | ✅ |
| Action item extraction | ✅ | ✅ | ✅ |
| Cross-meeting context (RAG) | ❌ | ❌ | ✅ |
| Contradiction detection | ❌ | ❌ | ✅ |
| Participation stats | Partial | Partial | ✅ |
| PII anonymization | ❌ | ❌ | ✅ |
| Local-first / private | ❌ | ❌ | ✅ |
| Open source | ❌ | ❌ | ✅ |

## 📜 License
MIT