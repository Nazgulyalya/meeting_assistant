from utils.logger import get_logger
logger = get_logger("orchestrator")

from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from agents.transcript_agent import TranscriptAgent, TranscriptOutput
from agents.memory_agent import MemoryAgent, MemoryResult
from agents.action_agent import ActionAgent, ActionOutput
from agents.synthesis_agent import SynthesisAgent, SynthesisOutput
from rag.vectorstore import MeetingVectorStore

import uuid
from datetime import datetime

# --- Shared State (передаётся между агентами) ---
class MeetingState(TypedDict):
    raw_input: str                          # исходный текст или транскрипт
    meeting_id: str
    transcript: Optional[TranscriptOutput]
    memory: Optional[MemoryResult]
    actions: Optional[ActionOutput]
    synthesis: Optional[SynthesisOutput]
    error: Optional[str]
    status: str                             # current step

# --- Узлы графа ---

transcript_agent = TranscriptAgent()
memory_agent = MemoryAgent()
action_agent = ActionAgent()
synthesis_agent = SynthesisAgent()
vector_store = MeetingVectorStore()

def run_transcript(state: MeetingState) -> MeetingState:
    logger.info("🎙️  Transcript Agent running...")
    try:
        result = transcript_agent.process(state["raw_input"])
        return {**state, "transcript": result, "status": "transcript_done"}
    except Exception as e:
        return {**state, "error": str(e), "status": "failed"}

def run_memory(state: MeetingState) -> MeetingState:
    logger.info("🧠  Memory Agent running...")
    try:
        transcript_text = state["transcript"].cleaned_transcript
        result = memory_agent.process(transcript_text)
        return {**state, "memory": result, "status": "memory_done"}
    except Exception as e:
        return {**state, "error": str(e), "status": "failed"}

def run_action(state: MeetingState) -> MeetingState:
    logger.info("✅  Action Agent running...")
    try:
        transcript_text = state["transcript"].cleaned_transcript
        memory_context = state["memory"].relevant_context if state["memory"] else ""
        result = action_agent.process(transcript_text, memory_context)
        return {**state, "actions": result, "status": "action_done"}
    except Exception as e:
        return {**state, "error": str(e), "status": "failed"}

def run_synthesis(state: MeetingState) -> MeetingState:
    logger.info("📝  Synthesis Agent running...")
    try:
        transcript_text = state["transcript"].cleaned_transcript
        memory_context = state["memory"].relevant_context if state["memory"] else ""
        result = synthesis_agent.process(transcript_text, state["actions"], memory_context)
        return {**state, "synthesis": result, "status": "synthesis_done"}
    except Exception as e:
        return {**state, "error": str(e), "status": "failed"}

def save_to_memory(state: MeetingState) -> MeetingState:
    """Save this meeting to ChromaDB for future RAG retrieval."""
    logger.info("💾  Saving to memory...")
    try:
        vector_store.add_meeting(
            meeting_id=state["meeting_id"],
            transcript=state["transcript"].cleaned_transcript,
            metadata={
                "date": datetime.now().strftime("%Y-%m-%d"),
                "title": state["synthesis"].email_subject
            }
        )
        return {**state, "status": "completed"}
    except Exception as e:
        # Non-critical — продолжаем даже если сохранение упало
        logger.info(f"Warning: could not save to memory: {e}")
        return {**state, "status": "completed"}

# --- Routing ---
def should_continue(state: MeetingState) -> str:
    if state.get("error"):
        return "end"
    return "continue"

# --- Граф ---
def build_graph():
    graph = StateGraph(MeetingState)

    graph.add_node("transcript", run_transcript)
    graph.add_node("memory", run_memory)
    graph.add_node("action", run_action)
    graph.add_node("synthesis", run_synthesis)
    graph.add_node("save", save_to_memory)

    graph.set_entry_point("transcript")

    graph.add_conditional_edges("transcript", should_continue,
        {"continue": "memory", "end": END})
    graph.add_conditional_edges("memory", should_continue,
        {"continue": "action", "end": END})
    graph.add_conditional_edges("action", should_continue,
        {"continue": "synthesis", "end": END})
    graph.add_conditional_edges("synthesis", should_continue,
        {"continue": "save", "end": END})
    graph.add_edge("save", END)

    return graph.compile()

# Глобальный граф — импортируем в UI
meeting_graph = build_graph()

from utils.cache import get_cached, set_cached

# --- Главная функция ---
def process_meeting(raw_transcript: str) -> MeetingState:
    cached = get_cached(raw_transcript)
    if cached:
        print("💾 Cache hit — returning cached result")
        return cached
    initial_state: MeetingState = {
        "raw_input": raw_transcript,
        "meeting_id": f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "transcript": None,
        "memory": None,
        "actions": None,
        "synthesis": None,
        "error": None,
        "status": "started"
    }
    result = meeting_graph.invoke(initial_state)
    if result.get("error") is None:
        set_cached(raw_transcript, result)
    return result