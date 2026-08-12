import streamlit as st

from hindsight_ops import (
    follow_ups,
    generate_briefing,
    recall_meetings,
    save_meeting,
)

st.set_page_config(page_title="MeetingMind", page_icon="🤖", layout="centered")

st.title("🤖 MeetingMind")
st.caption("Meeting memory & AI-powered briefings, backed by Hindsight.")

log_tab, prep_tab = st.tabs(["📝 Log a Meeting", "🧠 Meeting Prep"])

# ---------------------------------------------------------------------------
# Tab 1: Log a meeting
# ---------------------------------------------------------------------------
with log_tab:
    st.subheader("Save a meeting")

    with st.form("log_meeting_form", clear_on_submit=True):
        contact = st.text_input("Who was the meeting with?")
        notes = st.text_area("What happened in the meeting?", height=150)
        submitted = st.form_submit_button("Save to Hindsight", type="primary")

    if submitted:
        if not contact.strip() or not notes.strip():
            st.warning("Please fill in both the contact and the notes.")
        else:
            try:
                with st.spinner("Saving meeting to Hindsight..."):
                    save_meeting(contact.strip(), notes.strip())
                st.success(f"✓ Meeting with **{contact}** stored successfully!")
            except Exception as e:
                st.error(f"Couldn't save the meeting: {e}")

# ---------------------------------------------------------------------------
# Tab 2: Meeting prep
# ---------------------------------------------------------------------------
with prep_tab:
    st.subheader("Prep for an upcoming meeting")

    prep_contact = st.text_input("Who are you meeting next?", key="prep_contact")
    generate = st.button("Generate briefing", type="primary")

    if generate:
        if not prep_contact.strip():
            st.warning("Please enter who you're meeting.")
        else:
            person = prep_contact.strip()

            # --- Recall: relevant history + follow-ups -----------------
            try:
                with st.spinner("Searching Hindsight for previous interactions..."):
                    results = recall_meetings(person)
            except Exception as e:
                st.error(f"Couldn't recall memories: {e}")
                results = None

            if results is not None:
                st.markdown(f"### 📌 Relevant history — {person}")
                if results:
                    for result in results[:5]:
                        st.markdown(f"- {result.text}")
                else:
                    st.info("No relevant history found yet.")

                st.markdown("### ⚠️ Things to follow up on")
                items = follow_ups(results, limit=3)
                if items:
                    for item in items:
                        st.markdown(f"- {item}")
                else:
                    st.info("Nothing flagged as an outstanding follow-up.")

                st.markdown("### 💬 Suggested talking points")
                st.markdown(
                    f"- Ask {person} about any outstanding commitments.\n"
                    "- Review the decisions made in previous meetings.\n"
                    "- Confirm the next steps and deadlines."
                )

            st.divider()

            # --- Reflect: AI-generated briefing -------------------------
            st.markdown(f"### 🤖 AI meeting brief — {person}")
            try:
                with st.spinner("Generating briefing with Hindsight Reflect..."):
                    briefing = generate_briefing(person)
                st.markdown(briefing.text)
            except Exception as e:
                st.error(f"Couldn't generate the briefing: {e}")
