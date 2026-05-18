"""LLM-as-judge evaluation of generated outputs.

Uses a separate LLM call to score each agent's output against a rubric.
Provides quantitative quality metrics for the executive summary, action items, and email draft.
"""
import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

from orchestrator import process_meeting

EVAL_TRANSCRIPTS = [
    {
        "id": "eval_1",
        "text": """
Speaker A: Let's discuss Q3 priorities. We need to ship the new payments feature by September.
Speaker B: Sarah will lead engineering. I'll handle product specs.
Speaker A: Marketing campaign starts in August — Tom owns that.
Speaker C: Budget approved at 200k.
Speaker A: Open question — should we localize for European market in v1?
"""
    },
    {
        "id": "eval_2",
        "text": """
Speaker A: Security review for new auth system.
Speaker B: Three issues found — weak password policy, missing 2FA, session timeout.
Speaker A: Decision: enforce 2FA for all admins by next sprint.
Speaker C: I'll implement 2FA. Done by August 15th.
Speaker A: We also need to update privacy policy for new auth flow.
"""
    },
    {
        "id": "eval_3",
        "text": """
Speaker A: Customer churn jumped last month. Need to understand why.
Speaker B: Exit surveys show pricing as the top reason.
Speaker A: But pricing hasn't changed in 12 months.
Speaker C: Competitor X launched a cheaper tier in May.
Speaker A: Decision: launch SMB tier at 40% lower price by October.
Speaker B: Marketing will run a winback campaign starting next week.
"""
    },
]

JUDGE_PROMPT = """You are an expert evaluator. Score the following meeting analysis output on a 1-5 scale across 4 dimensions.

ORIGINAL TRANSCRIPT:
{transcript}

GENERATED OUTPUT:
Executive Summary: {summary}
Action Items: {action_items}
Decisions: {decisions}
Email Body: {email_body}

Score each from 1 (poor) to 5 (excellent):
- relevance: Does the output capture the key points from the transcript?
- completeness: Are all major action items and decisions covered?
- accuracy: Is information factually correct (no hallucinations)?
- format_quality: Is the output well-structured and usable?

Return ONLY a JSON object with these 4 scores and a one-sentence justification:
{{"relevance": N, "completeness": N, "accuracy": N, "format_quality": N, "comment": "..."}}
"""

def evaluate_outputs():
    judge = ChatGroq(model="llama-3.1-8b-instant", temperature=0,
                    api_key=os.getenv("GROQ_API_KEY"))

    results = []
    for case in EVAL_TRANSCRIPTS:
        print(f"\n[Eval {case['id']}] Running pipeline...")
        pipe = process_meeting(case["text"])
        if pipe.get("error"):
            print(f"  Pipeline error: {pipe['error']}")
            continue

        prompt = JUDGE_PROMPT.format(
            transcript=case["text"],
            summary="; ".join(pipe["synthesis"].executive_summary),
            action_items="; ".join([
                f"{a.task} ({a.owner})" for a in pipe["actions"].action_items
            ]),
            decisions="; ".join([d.decision for d in pipe["actions"].decisions]),
            email_body=pipe["synthesis"].email_body[:500]
        )

        response = judge.invoke(prompt)
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        try:
            score = json.loads(text)
            results.append({"id": case["id"], **score})
            print(f"  Scores: R={score['relevance']} C={score['completeness']} "
                  f"A={score['accuracy']} F={score['format_quality']}")
        except Exception as e:
            print(f"  Failed to parse judge: {e}")

    # Aggregate
    if results:
        avg = {
            "relevance": round(sum(r["relevance"] for r in results) / len(results), 2),
            "completeness": round(sum(r["completeness"] for r in results) / len(results), 2),
            "accuracy": round(sum(r["accuracy"] for r in results) / len(results), 2),
            "format_quality": round(sum(r["format_quality"] for r in results) / len(results), 2),
        }
        avg["overall"] = round(sum(avg.values()) / 4, 2)

        print("\n" + "=" * 50)
        print("AGGREGATE QUALITY SCORES (LLM-as-judge)")
        print("=" * 50)
        print(json.dumps(avg, indent=2))

        with open("evals/output_quality_results.json", "w") as f:
            json.dump({"aggregate": avg, "details": results}, f, indent=2)

        print("\n✅ Saved to evals/output_quality_results.json")
        return avg

if __name__ == "__main__":
    evaluate_outputs()