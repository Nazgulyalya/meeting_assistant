import streamlit as st
import sys
sys.path.append(".")

from orchestrator import process_meeting

st.set_page_config(
    page_title="Meeting Assistant",
    page_icon="🎤",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0F172A 0%, #1E1B4B 100%);
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #A78BFA;
    }
    h1, h2, h3 {
        color: #F1F5F9;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎤 Meeting Assistant")
st.caption("Multi-agent system for meeting analysis, action tracking, and follow-ups")

# --- Input ---
st.subheader("📋 Input Method")
input_method = st.radio("Choose input:", ["Paste text", "Upload audio"], horizontal=True)

transcript = ""
audio_file = None

if input_method == "Paste text":
    transcript = st.text_area("Raw transcript", height=200,
        placeholder="Speaker A: Let's start...")
else:
    audio_file = st.file_uploader("Upload audio (mp3/wav/m4a)",
        type=["mp3", "wav", "m4a"])

col1, col2 = st.columns([1, 3])
with col1:
    run_btn = st.button("▶️ Analyze Meeting", type="primary", use_container_width=True)

# --- Pipeline ---
if run_btn:
    if input_method == "Paste text" and not transcript.strip():
        st.error("Please paste a transcript first.")
    elif input_method == "Upload audio" and not audio_file:
        st.error("Please upload an audio file.")
    else:
        with st.spinner("Running multi-agent pipeline..."):
            if input_method == "Upload audio":
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tmp.write(audio_file.read())
                    tmp_path = tmp.name
                from agents.transcript_agent import TranscriptAgent
                agent = TranscriptAgent()
                transcript = agent.transcribe_audio(tmp_path)
                st.info(f"Transcribed: {transcript[:200]}...")
            result = process_meeting(transcript)
        if result["error"]:
            st.error(f"Pipeline error: {result['error']}")
        else:
            st.success("✅ Analysis complete!")
            st.session_state["result"] = result


# --- Results ---
if "result" in st.session_state:
    result = st.session_state["result"]
    synthesis = result["synthesis"]
    actions = result["actions"]
    memory = result["memory"]
    transcript_out = result["transcript"]

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📌 Summary", "✅ Actions", "🧠 Memory", "📧 Email", "📊 Stats"
    ])

    # --- Tab 1: Summary ---
    with tab1:
        st.subheader("Executive Summary")
        for bullet in synthesis.executive_summary:
            st.markdown(f"• {bullet}")

        st.divider()
        st.subheader("Full Summary")
        st.write(synthesis.full_summary)

        if memory.has_contradictions:
            st.warning(f"⚠️ Contradiction with past meetings: {memory.contradiction_notes}")

    # --- Tab 2: Action Items ---
    with tab2:
        st.subheader("Action Items")
        if actions.action_items:
            for item in actions.action_items:
                color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(item.priority, "⚪")
                conf = f"(confidence: {int(item.confidence * 100)}%)" if item.confidence < 0.8 else ""
                st.markdown(f"{color} **{item.task}**  \n👤 {item.owner} | 📅 {item.deadline} {conf}")
        else:
            st.info("No action items found.")

        st.divider()
        st.subheader("Decisions Made")
        for d in actions.decisions:
            st.markdown(f"✔️ {d.decision}")

        st.subheader("Open Questions")
        for q in actions.open_questions:
            st.markdown(f"❓ {q.question} *(raised by {q.raised_by})*")

    # --- Tab 3: Memory / Past Context ---
    with tab3:
        st.subheader("🧠 Relevant Past Context")
        st.write(memory.relevant_context)

        if memory.source_meetings:
            st.divider()
            st.subheader("📎 Sources Used (RAG retrieval)")
            for src in memory.source_meetings:
                st.markdown(f"- 📄 `{src}`")
            st.caption("These past meetings were retrieved from the knowledge base using semantic similarity.")

        if memory.has_contradictions:
            st.divider()
            st.error(f"⚠️ Contradiction Detected\n\n{memory.contradiction_notes}")
            st.caption("This is part of our explainability layer — the system flags when current decisions conflict with past ones.")

        st.divider()
        st.subheader("🔒 Privacy Check")
        from rag.pii_scrubber import detect_pii
        pii_found = detect_pii(transcript_out.cleaned_transcript)
        if pii_found:
            st.warning(f"PII detected (will be anonymized before storage): {pii_found}")
        else:
            st.success("✅ No PII detected in transcript")

    # --- Tab 4: Email Draft ---
    with tab4:
        st.subheader("Follow-up Email Draft")
        with st.expander("🔌 MCP Connection Status"):
            try:
                from mcp_client.client import list_mcp_tools
                tools = list_mcp_tools()
                st.success(f"✅ Connected to MCP server with {len(tools)} tools:")
                for t in tools:
                    st.markdown(f"- **{t['name']}**: {t['description'][:80]}")
            except Exception as e:
                st.error(f"MCP connection error: {e}")

        st.text_input("Subject", value=synthesis.email_subject, key="email_subject")
        email_body = st.text_area("Body", value=synthesis.email_body, height=300, key="email_body")

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            to_email = st.text_input("Send to (email)", placeholder="team@company.com")
        with col_b:
            st.write("")
            st.write("")
            send_btn = st.button("📧 Send via Gmail", type="primary")

        if send_btn:
            if not to_email:
                st.error("Please enter an email address.")
            else:
                with st.spinner("Sending email..."):
                    from mcp_client.client import send_email_via_mcp as send_email
                    result_send = send_email(
                        to=to_email,
                        subject=st.session_state["email_subject"],
                        body=st.session_state["email_body"]
                        )
                    
                if result_send["success"]:
                    st.success(f"✅ Email sent to {to_email}!")
                else:
                    st.error(f"Failed: {result_send['error']}")

        st.divider()
        st.subheader("📅 Schedule Follow-up Meeting")
        col_c, col_d = st.columns(2)
        with col_c:
            followup_date = st.date_input("Date")
            followup_time = st.time_input("Time")
        with col_d:
            attendees = st.text_input("Attendees (comma-separated emails)")
            cal_btn = st.button("📅 Create Calendar Event")

        if cal_btn:
            with st.spinner("Creating event..."):
                from mcp_client.client import create_event_via_mcp as create_event
                from datetime import datetime, timedelta
                start_dt = datetime.combine(followup_date, followup_time).isoformat()
                end_dt = datetime.combine(
                    followup_date,
                    followup_time.replace(hour=followup_time.hour + 1)
                ).isoformat()
                success = create_event(
                    title=synthesis.calendar_title,
                    description=synthesis.calendar_description,
                    start=start_dt,
                    end=end_dt,
                    attendees=[a.strip() for a in attendees.split(",") if a.strip()]
                )
            if success:
                st.success("✅ Calendar event created!")
            else:
                st.error("Failed to create event.")

    # --- Tab 5: Stats ---
    with tab5:
        st.subheader("Participation Stats")
        if actions.participation_stats:
            import pandas as pd
            df = pd.DataFrame([
                {"Speaker": s.speaker, "Words": s.word_count, "Talk Time %": s.talk_time_pct}
                for s in actions.participation_stats
            ])
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("Speaker")["Talk Time %"])
        else:
            st.info("No participation data.")

        st.divider()
        st.subheader("Transcript Details")
        st.write(f"**Language:** {transcript_out.language}")
        st.write(f"**Duration:** {transcript_out.duration_estimate}")
        if transcript_out.quality_warnings:
            for w in transcript_out.quality_warnings:
                st.warning(w)

        st.divider()
        st.subheader("⭐ Rate this analysis")
        rating = st.feedback("stars", key="rating")
        if rating is not None:
            st.caption(f"Thanks for rating! ({rating + 1}/5 stars)")