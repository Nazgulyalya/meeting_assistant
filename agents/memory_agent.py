from dotenv import load_dotenv
import os
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from rag.vectorstore import MeetingVectorStore
from pydantic import BaseModel
from typing import List

class MemoryResult(BaseModel):
    relevant_context: str        # синтез релевантного контекста
    source_meetings: List[str]   # какие митинги использованы
    has_contradictions: bool     # есть ли противоречия с прошлыми решениями
    contradiction_notes: str     # описание противоречий если есть

MEMORY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Meeting Memory Agent. Your job is to analyze the current meeting 
transcript and compare it with context retrieved from past meetings.

Your tasks:
1. Summarize what relevant past decisions, action items, or context are present
2. Identify if anything in the current meeting contradicts past decisions
3. List which past meetings are referenced

Return ONLY a JSON object with:
- relevant_context: string summarizing past relevant context
- source_meetings: list of meeting IDs referenced
- has_contradictions: boolean
- contradiction_notes: string explaining contradictions, or empty string if none

No text outside the JSON."""),
    ("human", """Current meeting transcript:
{current_transcript}

Retrieved past context:
{past_context}""")
])

class MemoryAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )
        self.store = MeetingVectorStore()
        self.chain = MEMORY_PROMPT | self.llm

    def process(self, current_transcript: str) -> MemoryResult:
        # Retrieve relevant past context
        results = self.store.query(current_transcript, n_results=5)

        if not results:
            return MemoryResult(
                relevant_context="No past meetings found in database.",
                source_meetings=[],
                has_contradictions=False,
                contradiction_notes=""
            )

        # Format retrieved chunks with source attribution
        past_context = "\n\n".join([
            f"[{r['meeting_id']}]: {r['text']}" for r in results
        ])

        response = self.chain.invoke({
            "current_transcript": current_transcript,
            "past_context": past_context
        })

        import json
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)
        return MemoryResult(**data)