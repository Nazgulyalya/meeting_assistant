"""Positive test cases — system works as expected."""
import pytest
from agents.transcript_agent import TranscriptAgent
from agents.action_agent import ActionAgent
from agents.memory_agent import MemoryAgent
from agents.synthesis_agent import SynthesisAgent
from rag.vectorstore import MeetingVectorStore
from rag.pii_scrubber import scrub_pii, detect_pii
from rag.chunker import chunk_text


SAMPLE_TRANSCRIPT = """
Speaker A: Let's start. John, can you finish the API by Friday?
Speaker B: Yes, Friday works.
Speaker A: Sarah, we decided to cancel dark mode.
Speaker C: What about the mobile bug?
Speaker A: Still open, medium priority.
"""


# --- Transcript Agent ---
def test_transcript_returns_valid_output():
    agent = TranscriptAgent()
    result = agent.process(SAMPLE_TRANSCRIPT)
    assert result.cleaned_transcript
    assert len(result.speakers) >= 2
    assert result.language

def test_transcript_detects_language():
    agent = TranscriptAgent()
    result = agent.process(SAMPLE_TRANSCRIPT)
    assert "english" in result.language.lower()


# --- Action Agent ---
def test_action_extracts_action_items():
    agent = ActionAgent()
    result = agent.process(SAMPLE_TRANSCRIPT)
    assert len(result.action_items) >= 1
    api_task = [a for a in result.action_items if "api" in a.task.lower()]
    assert len(api_task) >= 1
    assert "john" in api_task[0].owner.lower()

def test_action_extracts_decisions():
    agent = ActionAgent()
    result = agent.process(SAMPLE_TRANSCRIPT)
    assert len(result.decisions) >= 1

def test_action_extracts_open_questions():
    agent = ActionAgent()
    result = agent.process(SAMPLE_TRANSCRIPT)
    assert len(result.open_questions) >= 1

def test_action_calculates_participation():
    agent = ActionAgent()
    result = agent.process(SAMPLE_TRANSCRIPT)
    assert len(result.participation_stats) >= 2
    total_pct = sum(s.talk_time_pct for s in result.participation_stats)
    assert 95 <= total_pct <= 105  # ~100% allowing rounding


# --- Memory Agent / RAG ---
def test_memory_retrieves_past_context():
    agent = MemoryAgent()
    result = agent.process("Let's discuss mobile performance and API documentation")
    assert result.relevant_context
    assert len(result.source_meetings) > 0

def test_vector_store_count():
    store = MeetingVectorStore()
    assert store.count() > 10, "Need at least 10 chunks in DB — run seed_meetings.py"

def test_chunker_creates_overlapping_chunks():
    text = " ".join(["word"] * 500)
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1


# --- PII ---
def test_pii_scrubber_removes_email():
    text = "Email me at john@company.com"
    cleaned = scrub_pii(text)
    assert "[EMAIL]" in cleaned
    assert "john@company.com" not in cleaned

def test_pii_scrubber_removes_phone():
    text = "Call +1-555-123-4567"
    cleaned = scrub_pii(text)
    assert "[PHONE]" in cleaned

def test_pii_detection():
    text = "Contact john@email.com or call +1-555-0000"
    found = detect_pii(text)
    assert found.get("emails", 0) >= 1
    assert found.get("phones", 0) >= 1


# --- End-to-end ---
def test_full_pipeline():
    from orchestrator import process_meeting
    result = process_meeting(SAMPLE_TRANSCRIPT)
    assert result["error"] is None
    assert result["transcript"] is not None
    assert result["actions"] is not None
    assert result["synthesis"] is not None
    assert result["synthesis"].executive_summary
    assert result["synthesis"].email_body


import os, glob

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "data")
AUDIO_FILES = glob.glob(os.path.join(AUDIO_DIR, "*.mp3")) if os.path.isdir(AUDIO_DIR) else []

@pytest.mark.skipif(not AUDIO_FILES, reason="No audio files in tests/data/")
@pytest.mark.parametrize("audio_path", AUDIO_FILES)
def test_whisper_transcribes_audio(audio_path):
    """Each .mp3 in tests/data/ → Whisper → non-empty transcript."""
    agent = TranscriptAgent()
    raw = agent.transcribe_audio(audio_path)
    assert raw and len(raw.strip()) > 10, f"Empty transcript for {os.path.basename(audio_path)}"

@pytest.mark.skipif(not AUDIO_FILES, reason="No audio files in tests/data/")
@pytest.mark.parametrize("audio_path", AUDIO_FILES)
def test_audio_to_structured_output(audio_path):
    """Full audio pipeline for each file."""
    agent = TranscriptAgent()
    result = agent.process_audio(audio_path)
    assert result.cleaned_transcript
    assert result.language