"""Run this once to populate ChromaDB with sample past meetings."""
import sys
sys.path.append(".")

from rag.vectorstore import MeetingVectorStore

store = MeetingVectorStore()

meetings = [
    {
        "id": "meeting_2024_01_15",
        "date": "2024-01-15",
        "title": "Q1 Planning",
        "text": """
Speaker A: Let's align on Q1 priorities. The main goal is launching the new dashboard by March.
Speaker B: Agreed. Sarah will own the frontend, John takes the backend API.
Speaker A: We also decided to move from REST to GraphQL for the new endpoints.
Speaker B: The deadline for the first prototype is February 10th.
Speaker A: Mike, can you handle documentation? 
Speaker C: Yes, I'll have docs ready by February 5th.
Speaker A: Great. Budget approved for two new cloud servers.
"""
    },
    {
        "id": "meeting_2024_02_01",
        "date": "2024-02-01",
        "title": "Dashboard Progress Review",
        "text": """
Speaker A: Sarah, how's the frontend coming along?
Speaker B: About 60% done. There's a blocker — we need the API contract from John first.
Speaker C: John said the API spec will be ready by February 7th.
Speaker A: We also discussed moving the deadline to February 20th given the delays.
Speaker B: The design team approved the new color scheme last week.
Speaker A: Action item: John to share API contract by Feb 7. Sarah to complete UI by Feb 20.
"""
    },
    {
        "id": "meeting_2024_02_15",
        "date": "2024-02-15",
        "title": "Security Review",
        "text": """
Speaker A: We need to address the security audit findings before launch.
Speaker B: Three critical issues found: missing input validation, no rate limiting, weak auth tokens.
Speaker A: Decision: we delay launch by one week to fix these. New launch date March 8th.
Speaker C: I'll handle input validation and rate limiting. Should take 3 days.
Speaker B: I'll work on the auth token system. Done by February 22nd.
Speaker A: Also decided to bring in external security consultant for final review.
"""
    },
    {
        "id": "meeting_2024_03_01",
        "date": "2024-03-01",
        "title": "Pre-Launch Checklist",
        "text": """
Speaker A: One week to launch. Let's run through the checklist.
Speaker B: All security issues resolved. External audit passed.
Speaker C: Documentation complete and published.
Speaker A: Marketing campaign ready. Social posts scheduled for launch day.
Speaker B: Decided to do a soft launch first — invite-only for first 500 users.
Speaker A: Support team briefed. On-call rotation set up for launch week.
Speaker C: Performance tests show dashboard handles 1000 concurrent users fine.
"""
    },
    {
        "id": "meeting_2024_03_20",
        "date": "2024-03-20",
        "title": "Post-Launch Retrospective",
        "text": """
Speaker A: Launch went well overall. 2,000 signups in first week.
Speaker B: We had one incident — database timeout on March 12th, resolved in 40 minutes.
Speaker C: User feedback mostly positive. Top complaint: slow load on mobile.
Speaker A: Decision: mobile performance is Q2 priority number one.
Speaker B: We're moving sprint planning to Mondays starting next week.
Speaker A: John will lead the mobile optimization initiative.
Speaker C: Budget for Q2 approved. Hiring two frontend contractors.
"""
    },
]

for m in meetings:
    store.add_meeting(
        meeting_id=m["id"],
        transcript=m["text"],
        metadata={"date": m["date"], "title": m["title"]}
    )

print(f"\nTotal chunks in DB: {store.count()}")
print("Seed data loaded successfully!")