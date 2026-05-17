"""Seed ChromaDB with 15 diverse sample meetings across 4 domains."""
import sys
sys.path.append(".")

from rag.vectorstore import MeetingVectorStore

store = MeetingVectorStore()

MEETINGS = [
    # --- ENGINEERING ---
    {
        "id": "eng_2024_01_15_q1_planning",
        "domain": "engineering",
        "date": "2024-01-15",
        "title": "Q1 Engineering Planning",
        "text": """
Speaker A: Let's align on Q1 priorities. Main goal is launching the new dashboard by March.
Speaker B: Agreed. Sarah will own the frontend, John takes the backend API.
Speaker A: We decided to move from REST to GraphQL for new endpoints.
Speaker B: First prototype deadline is February 10th.
Speaker A: Mike, can you handle documentation?
Speaker C: Yes, docs ready by February 5th.
Speaker A: Budget approved for two new cloud servers.
"""
    },
    {
        "id": "eng_2024_02_01_dashboard_review",
        "domain": "engineering",
        "date": "2024-02-01",
        "title": "Dashboard Progress Review",
        "text": """
Speaker A: Sarah, how's the frontend coming along?
Speaker B: About 60% done. Blocker — we need the API contract from John first.
Speaker C: API spec will be ready by February 7th.
Speaker A: We're moving the deadline to February 20th given delays.
Speaker B: Design team approved the new color scheme.
Speaker A: Action item: John to share API contract by Feb 7. Sarah completes UI by Feb 20.
"""
    },
    {
        "id": "eng_2024_02_15_security_review",
        "domain": "engineering",
        "date": "2024-02-15",
        "title": "Security Audit Review",
        "text": """
Speaker A: We need to address security audit findings before launch.
Speaker B: Three critical issues: missing input validation, no rate limiting, weak auth tokens.
Speaker A: Decision: delay launch by one week. New date March 8th.
Speaker C: I'll handle input validation and rate limiting. Three days.
Speaker B: Auth token system done by February 22nd.
Speaker A: Also decided to bring external security consultant for final review.
"""
    },
    {
        "id": "eng_2024_03_20_post_launch",
        "domain": "engineering",
        "date": "2024-03-20",
        "title": "Post-Launch Retrospective",
        "text": """
Speaker A: Launch went well. 2000 signups in first week.
Speaker B: One incident — database timeout March 12th, resolved in 40 minutes.
Speaker C: Top complaint is slow mobile load.
Speaker A: Mobile performance is Q2 priority number one.
Speaker B: Moving sprint planning to Mondays starting next week.
Speaker A: John leads mobile optimization initiative.
Speaker C: Q2 budget approved. Hiring two frontend contractors.
"""
    },

    # --- MARKETING ---
    {
        "id": "mkt_2024_02_05_campaign_kickoff",
        "domain": "marketing",
        "date": "2024-02-05",
        "title": "Spring Campaign Kickoff",
        "text": """
Speaker A: Spring campaign launches April 1st. Theme is 'New Beginnings'.
Speaker B: Budget approved at 50k. Split 40/30/30 between social, email, paid ads.
Speaker C: I'll handle copy. First drafts by February 20th.
Speaker A: Decision: we're not using influencers this round — too expensive last time.
Speaker B: Email list needs cleanup. Anna will deduplicate by March 1st.
Speaker A: Performance target: 15 percent open rate, 3 percent conversion.
"""
    },
    {
        "id": "mkt_2024_03_10_campaign_progress",
        "domain": "marketing",
        "date": "2024-03-10",
        "title": "Campaign Progress Check",
        "text": """
Speaker A: Three weeks to launch. Where are we?
Speaker B: Copy approved. Visual assets 80 percent done.
Speaker C: Email list cleaned — 12k subscribers removed.
Speaker A: We need landing page from web team — that's the blocker.
Speaker B: I'll escalate to John in engineering today.
Speaker A: Decision: soft launch with 10 percent of list first to validate messaging.
"""
    },
    {
        "id": "mkt_2024_04_15_campaign_review",
        "domain": "marketing",
        "date": "2024-04-15",
        "title": "Campaign Results Review",
        "text": """
Speaker A: Two weeks post-launch. Numbers please.
Speaker B: Open rate 18 percent — above target.
Speaker C: Conversion 2.1 percent — below target of 3 percent.
Speaker A: What's the gap?
Speaker B: Landing page bounce rate too high — 65 percent.
Speaker A: Decision: A/B test landing page hero section next week.
Speaker C: I'll prepare three variants by April 22nd.
"""
    },

    # --- DESIGN ---
    {
        "id": "design_2024_02_10_brand_refresh",
        "domain": "design",
        "date": "2024-02-10",
        "title": "Brand Refresh Discussion",
        "text": """
Speaker A: It's been 4 years since last brand refresh. Time to revisit.
Speaker B: Research shows our current colors feel dated. Survey of 200 users.
Speaker A: Decision: full brand refresh, not just colors. Logo, typography, voice.
Speaker C: I'll create three direction concepts by March 1st.
Speaker B: We need legal review of new trademark — Sarah handles that.
Speaker A: Budget — 30k for design agency consultation if needed.
"""
    },
    {
        "id": "design_2024_03_05_concept_review",
        "domain": "design",
        "date": "2024-03-05",
        "title": "Brand Concepts Review",
        "text": """
Speaker A: Three concepts from the design team.
Speaker B: Concept A is bold but risky. Concept B safe. Concept C modern.
Speaker C: User testing showed 60 percent preferred Concept C.
Speaker A: Decision: go with Concept C. Mike finalizes by March 25th.
Speaker B: We need transition plan for old assets across website, app, docs.
Speaker A: Action: Mike creates transition plan by April 1st.
"""
    },
    {
        "id": "design_2024_04_20_rollout",
        "domain": "design",
        "date": "2024-04-20",
        "title": "Brand Rollout Planning",
        "text": """
Speaker A: Rollout starts May 1st. Status check.
Speaker B: Website redesign 90 percent done.
Speaker C: Mobile app redesign blocked — engineering capacity issue.
Speaker A: We'll phase mobile — launch web first, mobile in June.
Speaker B: PR team prepared brand reveal post for May 1st.
Speaker A: Internal team trained on new brand guidelines last week.
"""
    },

    # --- HR / OPERATIONS ---
    {
        "id": "hr_2024_01_20_hiring_plan",
        "domain": "hr",
        "date": "2024-01-20",
        "title": "2024 Hiring Plan",
        "text": """
Speaker A: We have headcount for 12 new hires this year.
Speaker B: Engineering wants 6, design 2, marketing 2, operations 2.
Speaker A: Decision: prioritize engineering hires in Q1 — that's the bottleneck.
Speaker C: I'll post 4 engineering roles by January 25th.
Speaker B: Average time-to-hire is 45 days — let's aim to reduce to 30.
Speaker A: Referral bonus increased from 500 to 2000 dollars to speed things up.
"""
    },
    {
        "id": "hr_2024_03_15_hiring_review",
        "domain": "hr",
        "date": "2024-03-15",
        "title": "Q1 Hiring Review",
        "text": """
Speaker A: Q1 hiring results.
Speaker B: 4 engineers hired, 1 designer. 7 to go for full year.
Speaker C: Time-to-hire dropped to 38 days — close to target.
Speaker A: Two open offers pending — should close by end of month.
Speaker B: Referral bonus drove 30 percent of new hires.
Speaker A: Decision: keep referral bonus at 2k for rest of year.
"""
    },
    {
        "id": "hr_2024_04_05_remote_policy",
        "domain": "hr",
        "date": "2024-04-05",
        "title": "Remote Work Policy Update",
        "text": """
Speaker A: Need to update remote work policy. Some confusion about expectations.
Speaker B: Currently hybrid — 3 days office, 2 days remote.
Speaker C: Survey shows 75 percent of employees prefer fully flexible.
Speaker A: Decision: move to fully flexible. Teams self-organize on office days.
Speaker B: Some leaders worry about culture — we'll add quarterly team offsites.
Speaker A: New policy effective June 1st. Anna drafts communication by May 10th.
"""
    },
    {
        "id": "hr_2024_05_15_compensation_review",
        "domain": "hr",
        "date": "2024-05-15",
        "title": "Mid-Year Compensation Review",
        "text": """
Speaker A: Mid-year compensation review. Market data attached.
Speaker B: Our engineering salaries are 8 percent below market median.
Speaker C: Marketing and design are competitive.
Speaker A: Decision: adjust engineering salaries by 5 percent across the board.
Speaker B: Total cost is approximately 180k annualized.
Speaker A: Effective July 1st. Mike communicates individually before then.
"""
    },
    {
        "id": "hr_2024_06_10_team_offsite",
        "domain": "hr",
        "date": "2024-06-10",
        "title": "Team Offsite Planning",
        "text": """
Speaker A: First quarterly offsite per new remote policy.
Speaker B: Proposed location is Portland. 3 days, end of July.
Speaker C: Budget 25k for 30 people including travel.
Speaker A: Decision: confirmed Portland, July 24-26.
Speaker B: I'll book venue by June 20th.
Speaker C: Agenda focuses on strategy alignment and team bonding.
"""
    },
]

print(f"Loading {len(MEETINGS)} meetings into ChromaDB...")
for m in MEETINGS:
    store.add_meeting(
        meeting_id=m["id"],
        transcript=m["text"],
        metadata={
            "date": m["date"],
            "title": m["title"],
            "domain": m["domain"]
        }
    )

print(f"\n✅ Total chunks in DB: {store.count()}")
print(f"✅ Domains covered: engineering, marketing, design, HR")