from dotenv import load_dotenv
import os
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List
from agents.action_agent import ActionOutput

class SynthesisOutput(BaseModel):
    executive_summary: List[str]   # 3-5 bullet points
    full_summary: str              # narrative paragraph
    email_subject: str
    email_body: str                # ready-to-send email
    calendar_title: str
    calendar_description: str
    follow_up_needed: bool

SYNTHESIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Meeting Synthesis Agent. You produce the final output of the meeting pipeline.

Given the transcript, extracted actions, and past context — generate:
1. executive_summary: list of 3-5 short bullet strings (key takeaways)
2. full_summary: one narrative paragraph summarizing the meeting
3. email_subject: subject line for follow-up email
4. email_body: professional follow-up email to send to participants, include action items and decisions
5. calendar_title: title for a follow-up meeting if needed
6. calendar_description: description for the calendar event
7. follow_up_needed: true if there are unresolved open questions or future deadlines, else false

If past context reveals contradictions with current decisions — mention them in full_summary.

Return ONLY a valid JSON object. No text outside the JSON."""),
    ("human", """Transcript:
{transcript}

Action items extracted:
{action_items}

Decisions made:
{decisions}

Open questions:
{open_questions}

Past meeting context:
{memory_context}""")
])

class SynthesisAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.2   # чуть выше для более живого текста
        )
        self.chain = SYNTHESIS_PROMPT | self.llm

    def process(
        self,
        transcript: str,
        actions: ActionOutput,
        memory_context: str = ""
    ) -> SynthesisOutput:

        # Форматируем action items в читаемый вид
        action_str = "\n".join([
            f"- {a.task} → {a.owner} by {a.deadline} [{a.priority}]"
            for a in actions.action_items
        ]) or "None"

        decisions_str = "\n".join([
            f"- {d.decision}" for d in actions.decisions
        ]) or "None"

        questions_str = "\n".join([
            f"- {q.question} (raised by {q.raised_by})"
            for q in actions.open_questions
        ]) or "None"

        response = self.chain.invoke({
            "transcript": transcript,
            "action_items": action_str,
            "decisions": decisions_str,
            "open_questions": questions_str,
            "memory_context": memory_context or "No past context."
        })

        import json
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)
        return SynthesisOutput(**data)