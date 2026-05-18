# 🔍 Meeting Assistant — Self-Review

## Architecture Decisions

### Why LangGraph for orchestration?
The task requires explicit state passing between agents and conditional routing on errors. A simple sequential chain would not allow skipping subsequent agents on failure, and a fully custom orchestrator would have meant reinventing state management. LangGraph provides explicit state, debuggable transitions, and the orchestration logic still lives in this project's code (`orchestrator.py`), not as a black-box service.

### Why Groq instead of OpenAI?
Cost was a hard constraint. Groq's free tier provides llama-3.1-8b at sub-second latency, which is sufficient for structured extraction. Temperature is set to 0 for deterministic extraction agents and 0.2 for the synthesis agent to produce slightly more natural prose. Switching to GPT-4o-mini is a one-line change if needed for higher-stakes use cases.

### Why local Whisper instead of API?
Privacy. A meeting transcription tool that sends audio to a third-party server is a non-starter for many teams. Local Whisper means audio never leaves the user's machine. The trade-off is a one-time 74MB model download.

### Why a custom MCP server?
The capstone requires MCP integration, and the existing community servers for Gmail and Calendar add external dependencies and lock in their tool schemas. Building a custom MCP server using Anthropic's official SDK keeps the implementation owned by this project, demonstrates understanding of the protocol, and allows extending with project-specific tools without forking external code. The server runs as a subprocess via stdio — a true MCP transport.

### Why ChromaDB and sentence-transformers locally?
Same privacy reasoning. No API calls means no quota limits and no data leaving the machine. sentence-transformers (`all-MiniLM-L6-v2`) is small and fast on CPU. For production at scale, this would be swapped for a hosted vector DB like pgvector or Pinecone.

## Code Quality

### Defensive parsing
LLM outputs are not stable. The same prompt with `temperature=0` can return JSON with field `decision` one time and `title` another. The Pydantic models in `action_agent.py` use `from_raw()` classmethods that handle these variations gracefully. This proved valuable during testing — fewer test failures and more robust runtime behavior.

### Error handling
Every agent in the LangGraph has a try/except boundary that writes to the state's `error` field. Conditional edges check this field and short-circuit the pipeline. The UI surfaces errors gracefully instead of crashing.

### Logging strategy
Logging is split into two layers: `utils/logger.py` writes structured logs to files for the audit trail, and LangSmith captures the LLM-specific traces. This separation lets system errors and LLM behavior be debugged independently.

### Caching
Identical transcripts return the cached result via a hash-based in-memory cache. For a single-user assistant this is sufficient; production would use Redis.

## Trade-offs

### Speaker labels via LLM instead of diarization
True speaker diarization (pyannote.audio) requires a GPU for reasonable latency and adds significant complexity. The current approach uses the LLM to label speakers from context, which works well when speakers are introduced by name and degrades otherwise. Documented as a known limitation.

### Streamlit instead of a custom frontend
Streamlit is opinionated and limits UI flexibility, but it provides a working UI quickly. For a portfolio project, integration depth matters more than frontend framework choice.

### PII regex + spaCy NER instead of full custom NER model
spaCy's pre-trained NER catches the most common entity types (PERSON, GPE, ORG) without training a custom model. Regex covers numeric PII (emails, phones, cards, SSN, IPs). A production version might layer in a domain-specific NER model trained on meeting data.

### One LLM family for all agents
Using the same Groq model for all four agents is simpler but suboptimal — the Synthesis Agent could benefit from a larger model for richer prose. Chose simplicity for the capstone.

### Synthetic seed data
Most seed meetings are LLM-generated to avoid the privacy concerns of using real corporate meeting data in a public repository. Three real public-domain transcripts (a Federal Reserve press conference, a UN ministerial roundtable, and a TED talk on Supreme Court argument) are included to validate the system on real text. The architecture works on any transcript.

## Quantitative Evaluation Results

Formal evaluation suites instead of manual inspection:

- **RAG retrieval:** Recall@5 = 1.0, Precision@5 = 0.28, MRR = 0.51 across 10 hand-curated queries. Recall@5 of 1.0 means every relevant past meeting is retrieved within the top 5 chunks.
- **Output quality (LLM-as-judge):** scored 1-5 across relevance, completeness, accuracy, and format quality. Aggregate score available in `evals/output_quality_results.json`.
- **Performance:** end-to-end pipeline latency measured in `evals/performance_results.json`. Cost per run is $0 on Groq free tier.

All metrics are reproducible — anyone can run the scripts under `evals/` to verify.

## What Could Be Improved

- **Streaming responses** in the UI — currently the user waits for the full pipeline before seeing anything. Streaming would significantly improve perceived performance.
- **Real diarization** via pyannote.audio for better speaker attribution on unfamiliar voices.
- **Structured output APIs** (like Groq's JSON mode) would eliminate most of the defensive parsing complexity.
- **A second-pass validator agent** would catch hallucinations more reliably than the current confidence self-reports.
- **Larger evaluation set** — 10 RAG queries and 3 output quality samples are small; more would give tighter confidence intervals.

## Honest Assessment

This project demonstrates all required capabilities: multi-agent architecture, RAG with measured quality, true MCP protocol, observability via LangSmith, comprehensive testing including adversarial cases, and PII protection. The differentiated features — cross-meeting memory and contradiction detection — solve real problems that commercial tools do not address. The trade-offs are documented honestly rather than glossed over. The system is functional, reproducible, and presentable.