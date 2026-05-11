from dotenv import load_dotenv
import os
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List, Optional

class ActionItem(BaseModel):
    task: str
    owner: str          # "Unknown" если не указан
    deadline: str       # "Not specified" если не указан
    priority: str       # "High" / "Medium" / "Low"
    confidence: float   # 0.0 - 1.0

class Decision(BaseModel):
    decision: str
    rationale: str = ""
    participants: List[str] = []

class OpenQuestion(BaseModel):
    question: str
    raised_by: str = "Unknown"

class ParticipationStat(BaseModel):
    speaker: str
    word_count: int
    talk_time_pct: float

class ActionOutput(BaseModel):
    action_items: List[ActionItem]
    decisions: List[Decision]
    open_questions: List[OpenQuestion]
    participation_stats: List[ParticipationStat]

ACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an Action Extraction Agent for meeting transcripts.

Extract the following from the transcript:
1. action_items: concrete tasks assigned to people (with owner, deadline, priority High/Medium/Low, confidence 0-1)
2. decisions: things that were formally decided (with rationale and who was involved)
3. open_questions: questions raised but not answered
4. participation_stats: count words per speaker, calculate percentage of total

Rules:
- If owner is unclear, use "Unknown"
- If deadline is unclear, use "Not specified"  
- Confidence < 0.7 means it's inferred, not explicit
- Count words per speaker from "Speaker X:" labels

Return ONLY a valid JSON object. No text outside the JSON."""),
    ("human", """Meeting transcript:
{transcript}

Additional context from past meetings:
{memory_context}""")
])

class ActionAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )
        self.chain = ACTION_PROMPT | self.llm

    def process(self, transcript: str, memory_context: str = "") -> ActionOutput:
        response = self.chain.invoke({
            "transcript": transcript,
            "memory_context": memory_context or "No past context available."
        })

        import json
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)

        # Если модель вернула participation_stats как dict — конвертируем в list
        stats = data.get("participation_stats", [])
        if isinstance(stats, dict):
            total = sum(stats.values()) or 1
            data["participation_stats"] = [
                {"speaker": k, "word_count": v, "talk_time_pct": round(v / total * 100, 1)}
                for k, v in stats.items()
            ]

        return ActionOutput(**data)