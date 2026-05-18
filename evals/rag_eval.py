"""RAG retrieval quality evaluation."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vectorstore import MeetingVectorStore
import json

# Query → expected meeting IDs that should be retrieved
EVAL_SET = [
    {
        "query": "mobile performance issues and optimization",
        "expected_ids": ["eng_2024_03_20_post_launch"],
    },
    {
        "query": "API documentation deadlines",
        "expected_ids": ["eng_2024_01_15_q1_planning", "eng_2024_02_01_dashboard_review"],
    },
    {
        "query": "security audit and authentication tokens",
        "expected_ids": ["eng_2024_02_15_security_review"],
    },
    {
        "query": "spring marketing campaign budget allocation",
        "expected_ids": ["mkt_2024_02_05_campaign_kickoff"],
    },
    {
        "query": "email open rates and conversion targets",
        "expected_ids": ["mkt_2024_02_05_campaign_kickoff", "mkt_2024_04_15_campaign_review"],
    },
    {
        "query": "brand refresh and new logo design",
        "expected_ids": ["design_2024_02_10_brand_refresh", "design_2024_03_05_concept_review"],
    },
    {
        "query": "engineering hiring plan and time to hire",
        "expected_ids": ["hr_2024_01_20_hiring_plan", "hr_2024_03_15_hiring_review"],
    },
    {
        "query": "remote work policy and flexible schedule",
        "expected_ids": ["hr_2024_04_05_remote_policy"],
    },
    {
        "query": "compensation review and salary adjustments",
        "expected_ids": ["hr_2024_05_15_compensation_review"],
    },
    {
        "query": "team offsite planning and venue",
        "expected_ids": ["hr_2024_06_10_team_offsite"],
    },
]

def evaluate_retrieval(k: int = 5):
    store = MeetingVectorStore()
    total_precision = 0
    total_recall = 0
    total_mrr = 0   # Mean Reciprocal Rank
    detailed = []

    for case in EVAL_SET:
        results = store.query(case["query"], n_results=k)
        retrieved_ids = list({r["meeting_id"] for r in results})
        expected_ids = set(case["expected_ids"])

        hits = expected_ids & set(retrieved_ids)
        precision = len(hits) / len(retrieved_ids) if retrieved_ids else 0
        recall = len(hits) / len(expected_ids) if expected_ids else 0

        # MRR — rank of first relevant result
        mrr = 0
        for idx, rid in enumerate(retrieved_ids):
            if rid in expected_ids:
                mrr = 1 / (idx + 1)
                break

        total_precision += precision
        total_recall += recall
        total_mrr += mrr

        detailed.append({
            "query": case["query"],
            "expected": list(expected_ids),
            "retrieved": retrieved_ids,
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "mrr": round(mrr, 2),
        })

    n = len(EVAL_SET)
    summary = {
        "evaluated_queries": n,
        "avg_precision_at_5": round(total_precision / n, 3),
        "avg_recall_at_5": round(total_recall / n, 3),
        "mean_reciprocal_rank": round(total_mrr / n, 3),
    }

    print("=" * 60)
    print("RAG RETRIEVAL EVALUATION")
    print("=" * 60)
    print(json.dumps(summary, indent=2))
    print("\nPer-query details:")
    for d in detailed:
        print(f"  Q: {d['query'][:50]}")
        print(f"     precision={d['precision']} recall={d['recall']} mrr={d['mrr']}")

    # Save to file
    os.makedirs("evals", exist_ok=True)
    with open("evals/results.json", "w") as f:
        json.dump({"summary": summary, "details": detailed}, f, indent=2)

    print(f"\n✅ Results saved to evals/results.json")
    return summary

if __name__ == "__main__":
    evaluate_retrieval(k=5)