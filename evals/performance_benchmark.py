"""Measure end-to-end latency and token usage."""
import sys, os, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import process_meeting

TRANSCRIPT = """
Speaker A: Welcome to the quarterly review. Three main topics today.
Speaker B: First — engineering delivered all Q3 commitments on time.
Speaker C: Second — marketing campaign hit 18% open rate, target was 15%.
Speaker A: Third — we need to discuss Q4 hiring. Six open roles.
Speaker B: I propose accelerating two of the senior engineering hires.
Speaker A: Decision: yes, prioritize seniors. Anna handles recruiting.
Speaker C: Budget impact is 200k for Q4 only.
Speaker A: Approved. Any open questions before we wrap?
Speaker B: What about the security audit results?
Speaker A: Good catch — let's schedule a separate session next week.
"""

def benchmark(runs: int = 3):
    timings = []
    for i in range(runs):
        print(f"\nRun {i+1}/{runs}...")
        start = time.time()
        result = process_meeting(TRANSCRIPT)
        elapsed = time.time() - start
        if result.get("error"):
            print(f"  Error: {result['error']}")
            continue
        timings.append(elapsed)
        print(f"  Latency: {elapsed:.2f}s")

    if timings:
        avg = sum(timings) / len(timings)
        print("\n" + "=" * 40)
        print(f"AVG end-to-end latency: {avg:.2f}s over {len(timings)} runs")
        print(f"Min: {min(timings):.2f}s | Max: {max(timings):.2f}s")
        print("=" * 40)
        print(f"\nTokens used: visible in LangSmith dashboard")
        print(f"Estimated cost: $0 (Groq free tier)")

        import json
        with open("evals/performance_results.json", "w") as f:
            json.dump({
                "avg_latency_sec": round(avg, 2),
                "min_latency_sec": round(min(timings), 2),
                "max_latency_sec": round(max(timings), 2),
                "runs": len(timings),
                "cost_per_run_usd": 0.0,
            }, f, indent=2)

if __name__ == "__main__":
    benchmark()