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

    # --- LEGAL / COMPLIANCE ---
    {
        "id": "legal_2024_02_10_gdpr_review",
        "domain": "legal",
        "date": "2024-02-10",
        "title": "GDPR Compliance Review",
        "text": """
Speaker A: Annual GDPR review. Status check on data handling.
Speaker B: User data retention policy is current. 24 month maximum.
Speaker C: We had two data subject access requests last quarter, both fulfilled within deadline.
Speaker A: Decision: implement automated DSAR workflow by end of Q2.
Speaker B: Privacy policy needs update for new analytics vendor.
Speaker A: Anna handles privacy policy update by March 15th.
"""
    },
    {
        "id": "legal_2024_03_20_contract_template",
        "domain": "legal",
        "date": "2024-03-20",
        "title": "Vendor Contract Template Update",
        "text": """
Speaker A: Our vendor contract template is 4 years old. Time for refresh.
Speaker B: Key changes needed: AI clauses, data processing addendum, force majeure.
Speaker A: Decision: external counsel will draft new template by April 30th.
Speaker C: Budget approved for outside counsel, 15k.
Speaker B: All new contracts after May 1st use the new template.
"""
    },
    {
        "id": "legal_2024_04_15_ip_policy",
        "domain": "legal",
        "date": "2024-04-15",
        "title": "IP Policy for AI-Generated Content",
        "text": """
Speaker A: We need policy on AI-generated work. Employees asking questions.
Speaker B: Current copyright law is ambiguous for AI output.
Speaker A: Decision: any AI-assisted work must be reviewed and approved by human author.
Speaker C: All AI tools require approval from legal before use on client work.
Speaker A: Training session for all employees by end of May.
"""
    },

    # --- SALES ---
    {
        "id": "sales_2024_01_25_q1_targets",
        "domain": "sales",
        "date": "2024-01-25",
        "title": "Q1 Sales Targets",
        "text": """
Speaker A: Q1 target is 1.2M in new ARR.
Speaker B: Pipeline currently at 3.5M weighted. Looks healthy.
Speaker C: Enterprise team has 4 deals over 100k in late stage.
Speaker A: Decision: focus on upmarket deals — better margins.
Speaker B: New SDR starting February 1st. Will help with outbound.
Speaker A: Commissions accelerator kicks in at 110 percent of quota.
"""
    },
    {
        "id": "sales_2024_03_30_q1_review",
        "domain": "sales",
        "date": "2024-03-30",
        "title": "Q1 Sales Review",
        "text": """
Speaker A: Q1 closed. 1.35M ARR, 112 percent of target.
Speaker B: Three of four enterprise deals closed.
Speaker C: One deal slipped to Q2 — procurement delay.
Speaker A: Win rate 28 percent, up from 22 percent last quarter.
Speaker B: Lost deal analysis — pricing was main objection in 4 of 7 losses.
Speaker A: Decision: revise pricing tiers for SMB segment by April 15th.
"""
    },
    {
        "id": "sales_2024_05_20_competitive_analysis",
        "domain": "sales",
        "date": "2024-05-20",
        "title": "Competitive Analysis Update",
        "text": """
Speaker A: New competitor entering our space. Funded series A.
Speaker B: Their pricing is 30 percent below us. Faster setup time.
Speaker C: Our advantage is enterprise security features.
Speaker A: Decision: create battle card by next Friday.
Speaker B: Sales engineering trains team on new positioning.
Speaker A: We'll add competitive intelligence to weekly sales standup.
"""
    },

    # --- FINANCE ---
    {
        "id": "finance_2024_01_10_budget_planning",
        "domain": "finance",
        "date": "2024-01-10",
        "title": "2024 Budget Planning",
        "text": """
Speaker A: Annual budget review. Revenue projection 5.5M.
Speaker B: Engineering wants 2.2M, sales 1.8M, marketing 800k.
Speaker A: Decision: approved as proposed, with 5 percent contingency reserve.
Speaker C: Cash runway 18 months at current burn.
Speaker A: Quarterly budget reviews going forward, not annual only.
"""
    },
    {
        "id": "finance_2024_04_10_q1_close",
        "domain": "finance",
        "date": "2024-04-10",
        "title": "Q1 Financial Close",
        "text": """
Speaker A: Q1 numbers final. Revenue 1.4M, slightly above plan.
Speaker B: Burn rate 380k per month, within budget.
Speaker C: AR aging is concerning — 90k over 60 days.
Speaker A: Decision: implement net 30 terms for new customers, was net 60.
Speaker B: Collections cycle should improve by 15 days.
Speaker A: Audit prep starts next month for annual review.
"""
    },
    {
        "id": "finance_2024_06_25_funding_strategy",
        "domain": "finance",
        "date": "2024-06-25",
        "title": "Series B Funding Strategy",
        "text": """
Speaker A: Series B planning. Targeting close in Q4.
Speaker B: Three VCs expressed interest after recent metrics.
Speaker C: We need 24 months of runway in projections.
Speaker A: Target raise 15M at 80M post.
Speaker B: Decision: hire investment banker to run process — David handles selection.
Speaker A: Data room preparation starts in July.
"""
    },

    # --- CUSTOMER SUPPORT ---
    {
        "id": "support_2024_02_20_ticket_volume",
        "domain": "support",
        "date": "2024-02-20",
        "title": "Ticket Volume Review",
        "text": """
Speaker A: Ticket volume up 40 percent month over month.
Speaker B: Most tickets are about new dashboard — confusion on navigation.
Speaker C: First response time degraded to 6 hours, target is 4.
Speaker A: Decision: invest in self-service knowledge base.
Speaker B: Two support engineers starting next month, will reduce load.
Speaker A: Product team creates in-app tutorials by end of March.
"""
    },
    {
        "id": "support_2024_04_25_csat_improvement",
        "domain": "support",
        "date": "2024-04-25",
        "title": "CSAT Improvement Plan",
        "text": """
Speaker A: CSAT dropped to 72 percent. Target is 85 percent.
Speaker B: Main complaints are slow resolution and lack of follow-up.
Speaker C: We're implementing case ownership model.
Speaker A: Decision: every case has named owner end to end.
Speaker B: 24-hour follow-up rule on all resolved cases.
Speaker A: Mike rolls this out, expects CSAT recovery in 6 weeks.
"""
    },
    {
        "id": "support_2024_06_05_ai_chatbot",
        "domain": "support",
        "date": "2024-06-05",
        "title": "AI Chatbot Pilot Review",
        "text": """
Speaker A: 30 days into AI chatbot pilot.
Speaker B: 35 percent of tickets resolved without human escalation.
Speaker C: User satisfaction with bot interactions is 78 percent.
Speaker A: Some edge cases still need work — billing questions especially.
Speaker B: Decision: continue rollout, expand to billing in Q3.
Speaker A: Project ROI looks strong — 200k annualized savings.
"""
    },

    # --- BACKLOG / OTHER ENGINEERING ---
    {
        "id": "eng_2024_05_10_api_v2",
        "domain": "engineering",
        "date": "2024-05-10",
        "title": "API v2 Planning",
        "text": """
Speaker A: Time to plan API v2. Current API has scaling issues.
Speaker B: GraphQL migration partial, completing it makes sense.
Speaker C: Versioning strategy — header-based or URL-based?
Speaker A: Decision: URL-based versioning, cleaner for clients.
Speaker B: Deprecation policy — v1 supported 12 months after v2 launch.
Speaker A: First v2 endpoints in beta by August.
"""
    },
    {
        "id": "eng_2024_06_15_observability",
        "domain": "engineering",
        "date": "2024-06-15",
        "title": "Observability Stack Review",
        "text": """
Speaker A: Current monitoring spread across 4 tools. Too fragmented.
Speaker B: Datadog covers most needs. Sentry for errors. Costs 4k per month.
Speaker C: Decision: consolidate to Datadog. Decommission others by August.
Speaker B: Estimated savings 1.5k per month.
Speaker A: Need to migrate dashboards — Alex owns by July 20th.
"""
    },
    {
        "id": "eng_2024_07_01_security_incident",
        "domain": "engineering",
        "date": "2024-07-01",
        "title": "Security Incident Post-Mortem",
        "text": """
Speaker A: Last week's incident — auth token leak in logs.
Speaker B: Root cause: debug logging enabled in production for one hour.
Speaker C: All tokens rotated, no evidence of misuse.
Speaker A: Decision: log scrubbing required for all sensitive fields.
Speaker B: Production debug logging requires VP approval going forward.
Speaker A: We'll add this to security training for all engineers.
"""
    },


]

# --- REAL PUBLIC-DOMAIN TRANSCRIPTS ---
import os
REAL_DIR = os.path.join(os.path.dirname(__file__), "real_meetings")

REAL_MEETINGS = [
    {
        "id": "real_fed_press_2026_01_28",
        "domain": "finance",
        "date": "2026-01-28",
        "title": "Federal Reserve Press Conference - Powell",
        "source": "public_domain",
        "file": "fed_press_2026_01_28.txt",
    },
    {
        "id": "real_un_ministerial_2023",
        "domain": "government",
        "date": "2023-04-01",
        "title": "UN Ministerial Roundtable - Science & Innovation",
        "source": "public_domain",
        "file": "un_ministerial_2023.txt",
    },
    {
        "id": "real_ted_supreme_court",
        "domain": "legal",
        "date": "2025-11-01",
        "title": "TED Talk - Supreme Court Case Argument",
        "source": "public_domain",
        "file": "ted_supreme_court.txt",
    },
]

for m in REAL_MEETINGS:
    path = os.path.join(REAL_DIR, m["file"])
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        store.add_meeting(
            meeting_id=m["id"],
            transcript=text,
            metadata={
                "date": m["date"],
                "title": m["title"],
                "domain": m["domain"],
                "source": m["source"],
            }
        )
        print(f"✅ Loaded real public-domain transcript: {m['id']}")

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