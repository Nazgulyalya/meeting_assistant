# 📋 Meeting Assistant — Executive Summary

## The Problem
Modern teams hold thousands of meetings, but the value of those meetings evaporates within days. Action items get lost, decisions are forgotten, and there is no institutional memory connecting today's discussion to last month's commitment. Existing tools like Otter.ai and Fireflies have solved transcription, but they treat each meeting as an island — leaving the most painful problems untouched: context loss, follow-up automation, and privacy.

## The Solution
Meeting Assistant is a multi-agent AI system that transforms meeting audio or text into structured insights and automated follow-ups. It produces an executive summary with cross-meeting context, tracked action items with owners and confidence scores, a ready-to-send follow-up email, an auto-generated calendar event for the next meeting, and participation analytics showing voice balance across the team.

Four specialized agents (Transcript, Memory, Action, Synthesis) are orchestrated through LangGraph. The system uses retrieval-augmented generation (RAG) over a knowledge base of past meetings to surface relevant prior decisions and flag contradictions. Gmail and Google Calendar are connected through a custom Model Context Protocol (MCP) server, so the user can act on the output without leaving the app.

## Key Technical Highlights
- **Multi-agent architecture** with four agents sharing state through a LangGraph stateful graph owned by this project, not delegated to a third-party orchestrator.
- **Local-first RAG pipeline** using ChromaDB and local sentence-transformers embeddings. Meeting data is anonymized through regex and spaCy NER before being stored.
- **Real MCP protocol** integration via a custom MCP server (built on Anthropic's MCP SDK) that exposes Gmail and Calendar tools over JSON-RPC stdio.
- **Full observability** via LangSmith showing token usage, latency, and traces for every agent call.
- **Comprehensive evaluation suite:** RAG retrieval metrics (Recall@5 = 1.0), LLM-as-judge scoring for output quality, and latency benchmarks for performance — all reproducible.
- **Test coverage:** 26+ pytest cases including positive flows, edge cases, adversarial prompt injection, and real audio sample tests.

## Business Value
- **Time savings:** approximately 30 minutes per meeting in summary writing, follow-up emails, and calendar admin.
- **Information retention:** cross-meeting RAG prevents repeating discussions or missing prior commitments.
- **Inclusivity:** participation analytics surface team members who were not heard.
- **Privacy:** PII anonymization with regex and NER, combined with local-first processing, makes the system viable for regulated industries.
- **Cost:** built entirely on free-tier services (Groq, LangSmith, local Whisper) — zero ongoing infrastructure cost.

## Differentiation
Where commercial tools transcribe, this system reasons across meetings. It can answer questions like "What did we decide about the dashboard last month and does it contradict today's plan?" — a capability no major competitor currently provides.

## Next Steps
- Real speaker diarization through pyannote.audio for better attribution on unfamiliar voices.
- Multi-tenant deployment with OAuth2 authentication for team usage.
- Additional MCP connectors (Slack, Notion, Jira) to integrate with team task trackers.
- Fine-tuning prompts on team-specific jargon to improve extraction accuracy.
- Streaming responses in the UI for better perceived performance.