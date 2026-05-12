from orchestrator import process_meeting

sample_transcript = """
okay so let's kick off our weekly sync
yeah sure so i wanted to bring up the mobile performance issue
right we talked about this being a Q2 priority last time
exactly so sarah can you take ownership of mobile optimization
sure i can have a first pass done by end of next week
great and john what's the status on the api documentation
i havent started yet honestly
okay that's overdue let's make that high priority due this friday
also we decided to cancel the dark mode feature entirely
too much effort for too little value
agreed. any open questions?
yeah what happens with the two contractors we hired for dark mode
good point that's not resolved yet
okay let's note that as an open item
"""

print("Starting end-to-end pipeline...\n")
result = process_meeting(sample_transcript)

if result["error"]:
    print(f"❌ Error: {result['error']}")
else:
    print("\n✅ Pipeline completed!\n")
    print("=== EXECUTIVE SUMMARY ===")
    for b in result["synthesis"].executive_summary:
        print(f"  • {b}")

    print("\n=== ACTION ITEMS ===")
    for a in result["actions"].action_items:
        print(f"  - {a.task} → {a.owner} by {a.deadline} [{a.priority}]")

    print("\n=== OPEN QUESTIONS ===")
    for q in result["actions"].open_questions:
        print(f"  ? {q.question}")

    print("\n=== PAST CONTEXT USED ===")
    print(result["memory"].relevant_context[:300])

    print("\n=== EMAIL DRAFT ===")
    print(f"Subject: {result['synthesis'].email_subject}")
    print(result["synthesis"].email_body)