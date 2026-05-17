from dotenv import load_dotenv
import os
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Optional

# --- Модель выходных данных ---
class TranscriptOutput(BaseModel):
    cleaned_transcript: str        # чистый текст с метками спикеров
    speakers: list[str]            # список спикеров
    language: str                  # определённый язык
    duration_estimate: str         # примерная длина митинга
    quality_warnings: list[str]    # предупреждения (шум, неразборчиво и т.д.)

# --- Промпт ---
TRANSCRIPT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a transcript cleaning and structuring agent.

Your job:
1. Take raw meeting text and clean it up
2. Label speakers as Speaker A, Speaker B, etc. (or use names if mentioned)
3. Fix obvious typos and grammatical noise
4. Flag unclear or uncertain segments with [UNCLEAR]
5. Detect the language of the meeting
6. Estimate duration based on word count (~130 words per minute)
7. Note any quality warnings (heavy accent mentioned, background noise indicated, etc.)

Return ONLY a JSON object with these fields:
- cleaned_transcript: the full cleaned transcript with speaker labels
- speakers: list of speaker identifiers found
- language: detected language (e.g. "English", "Russian")
- duration_estimate: e.g. "~8 minutes"
- quality_warnings: list of warnings, empty list if none

Do not add any text outside the JSON."""),
    ("human", "Raw transcript:\n\n{raw_transcript}")
])

# --- Агент ---
class TranscriptAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )
        self.chain = TRANSCRIPT_PROMPT | self.llm

    def process(self, raw_transcript: str) -> TranscriptOutput:
        """
        Takes raw transcript text, returns structured TranscriptOutput.
        """
        if not raw_transcript or not raw_transcript.strip():
            raise ValueError("Transcript is empty or None")

        # Sanitize input — базовая защита от prompt injection
        sanitized = self._sanitize_input(raw_transcript)

        response = self.chain.invoke({"raw_transcript": sanitized})

        # Parse JSON from response — robust extraction
        import json
        text = response.content.strip()

        # Найти позицию первой {
        start = text.find("{")
        if start == -1:
            raise ValueError(f"No JSON found in response. Raw: {response.content[:300]}")

        try:
            data, _ = json.JSONDecoder().raw_decode(text[start:])
            return TranscriptOutput(**data)
        except Exception as e:
            raise ValueError(f"Failed to parse agent response: {e}\nRaw: {response.content[:500]}")

    def _sanitize_input(self, text: str) -> str:
        """Basic input sanitization against prompt injection."""
        # Удаляем попытки инъекций
        dangerous_phrases = [
            "ignore previous instructions",
            "ignore all instructions",
            "disregard the above",
            "you are now",
            "forget everything"
        ]
        lower = text.lower()
        for phrase in dangerous_phrases:
            if phrase in lower:
                text = text.replace(phrase, "[REDACTED]")
        return text
    
    def transcribe_audio(self, audio_path: str) -> str:
        """Convert audio file to raw transcript using Whisper."""
        import whisper
        model = whisper.load_model("base")  # base = 74MB, быстро
        result = model.transcribe(audio_path)
        return result["text"]

    def process_audio(self, audio_path: str) -> TranscriptOutput:
        """Full pipeline: audio → raw text → cleaned transcript."""
        raw_text = self.transcribe_audio(audio_path)
        return self.process(raw_text)