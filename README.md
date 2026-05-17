# 🎤 Meeting Assistant — Multi-Agent System

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

## 🏗️ Architecture
Audio/Text → Transcript Agent → Memory Agent (RAG) → Action Agent → Synthesis Agent → MCP (Gmail/Calendar)

Four agents orchestrated via LangGraph, each with distinct responsibilities. ChromaDB stores past meetings for semantic retrieval. All processing runs locally except LLM calls (Groq, free tier).

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