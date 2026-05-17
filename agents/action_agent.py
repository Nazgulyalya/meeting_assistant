from dotenv import load_dotenv
import os
import json
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List, Optional

class ActionItem(BaseModel):
    task: str = ""
    owner: str = "Unknown"
    deadline: str = "Not specified"
    priority: str = "Medium"
    confidence: float = 1.0

    @classmethod
    def from_raw(cls, data: dict) -> "ActionItem":
        return cls(
            task=data.get("task") or data.get("description") or data.get("action") or "",
            owner=data.get("owner") or data.get("assignee") or "Unknown",
            deadline=data.get("deadline") or data.get("due") or "Not specified",
            priority=data.get("priority") or "Medium",
            confidence=float(data.get("confidence", 1.0))
        )

class Decision(BaseModel):
    decision: str = ""
    rationale: str = ""
    participants: List[str] = []

    @classmethod
    def from_raw(cls, data: dict) -> "Decision":
        decision = (data.get("decision") or data.get("title") or
                    data.get("summary") or data.get("description") or "")
        participants = data.get("participants") or data.get("involved") or []
        if isinstance(participants, str):
            participants = [p.strip() for p in participants.split(",")]
        return cls(
            decision=decision,
            rationale=data.get("rationale") or "",
            participants=participants
        )

class OpenQuestion(BaseModel):
    question: str
    raised_by: str = "Unknown"

class ParticipationStat(BaseModel):
    speaker: str
    word_count: int
    talk_time_pct: float

class ActionOutput(BaseModel):
    action_items: List[ActionItem] = []
    decisions: List[Decision] = []
    open_questions: List[OpenQuestion] = []
    participation_stats: List[ParticipationStat] = []

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
- For decisions, always use the field name "decision" (not "title" or "summary")
- For decisions participants, always use a list of strings

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

        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)

        # Гарантируем что все списки есть
        for key in ["action_items", "decisions", "open_questions", "participation_stats"]:
            if key not in data or data[key] is None:
                data[key] = []

        # Нормализуем action_items
        if "action_items" in data:
            data["action_items"] = [ActionItem.from_raw(a) for a in data["action_items"]]

        
        # Нормализуем decisions
        if "decisions" in data:
            data["decisions"] = [Decision.from_raw(d) for d in data["decisions"]]
            

        # Нормализуем open_questions — иногда модель возвращает строки
        if "open_questions" in data:
            normalized_q = []
            for q in data["open_questions"]:
                if isinstance(q, str):
                    normalized_q.append({"question": q, "raised_by": "Unknown"})
                elif isinstance(q, dict):
                    normalized_q.append({
                        "question": q.get("question", ""),
                        "raised_by": q.get("raised_by") or q.get("asker") or "Unknown"
                    })
            data["open_questions"] = normalized_q

        # Нормализуем participation_stats — иногда word_count float
        stats = data.get("participation_stats", [])
        if isinstance(stats, dict):
            total = sum(stats.values()) or 1
            data["participation_stats"] = [
                {"speaker": k, "word_count": int(v), "talk_time_pct": round(v / total * 100, 1)}
                for k, v in stats.items()
            ]
        elif isinstance(stats, list):
            for s in stats:
                if "word_count" in s:
                    s["word_count"] = int(s["word_count"])

        return ActionOutput(**data)