import streamlit as st

from tools.analyzer import analyze_job
from tools.analyzer import stream_decision_summary
from rag.indexer import file_fingerprint, needs_rebuild, build_index_from_bytes
from rag.store import index_exists, load_index_meta
from prompts.preferences import load_preferences, save_preferences, reset_preferences

st.set_page_config(page_title="Job Match Advisor", page_icon="💼")
st.title("💼 Job Match Advisor")
st.write("Paste the job posting, and I'll analyze it and compare it with your CV.")


# --- CV ---------------------------------------------------------------------

with st.sidebar:
    st.header("Your CV")

    uploaded = st.file_uploader("Upload your CV (PDF)", type="pdf")

    if uploaded is not None:
        cv_bytes = uploaded.getvalue()
        fingerprint = file_fingerprint(cv_bytes)

        # Streamlit reruns the script on every interaction, so remember which
        # file this session already checked and skip the work entirely.
        if st.session_state.get("cv_fingerprint") == fingerprint:
            st.success("Current CV is ready.")
        elif not needs_rebuild(fingerprint):
            st.session_state["cv_fingerprint"] = fingerprint
            st.success("Current CV is ready - the index already matches it.")
        else:
            with st.status("Building the CV index...", expanded=True) as status:
                st.write("Extracting text...")
                st.write("Chunking and embedding...")
                chunk_count = build_index_from_bytes(cv_bytes, uploaded.name)
                status.update(
                    label=f"Index ready - {chunk_count} chunks",
                    state="complete",
                    expanded=False,
                )
            st.session_state["cv_fingerprint"] = fingerprint

    meta = load_index_meta()
    if index_exists():
        name = meta.get("source_name") or "an earlier build"
        st.caption(f"Indexed CV: {name} ({meta.get('chunk_count', '?')} chunks)")
    else:
        st.warning("No CV indexed yet. Upload a PDF to get started.")

    st.divider()
    st.header("Your requirements")

    with st.expander("Edit requirements", expanded=False):
        st.caption(
            "Deal breakers - a posting that explicitly breaks one of these is "
            "rejected however well the skills match. Leave empty to judge on "
            "skills alone."
        )
        edited_prefs = st.text_area(
            "Preferences",
            value=load_preferences(),
            height=180,
            label_visibility="collapsed",
            placeholder="e.g. The job must be On-site in Cairo, Egypt.",
        )

        p_save, p_reset = st.columns(2)
        if p_save.button("Save", use_container_width=True, key="save_prefs"):
            save_preferences(edited_prefs)
            st.success("Saved. The next analysis will use these requirements.")
        if p_reset.button("Reset to default", use_container_width=True, key="reset_prefs"):
            reset_preferences()
            st.rerun()


# --- Job posting ------------------------------------------------------------

job_text = st.text_area(
    label="Job Description",
    height=300,
    placeholder="Paste the job description here...",
)

analyze_clicked = st.button("Analyze Job", type="primary", disabled=not index_exists())


if analyze_clicked and job_text.strip():
    with st.status("Analyzing the job...", expanded=True) as status:
        st.write("📄 Extracting job requirements...")
        st.write("🔍 Looking for evidence in the CV...")
        st.write("⚖️ Making the decision...")

        decision = analyze_job(job_text)
        status.update(label="Analysis complete ✅", state="complete", expanded=False)

    if decision is None:
        st.error("Claude did not return a structured decision. Please try again.")
    else:
        st.session_state["decision"] = decision
        st.session_state["summary"] = None


# --- Result -----------------------------------------------------------------

COLORS = {"apply": "green", "apply_with_caution": "orange", "do_not_apply": "red"}
LABELS = {
    "apply": "Apply",
    "apply_with_caution": "Apply with caution",
    "do_not_apply": "Do not apply",
}

# A result stored by an older version of the app can outlive a code change,
# because session state survives a rerun. Drop it rather than render a value
# this version no longer understands.
stored = st.session_state.get("decision")
if stored and stored.get("decision") not in LABELS:
    st.session_state.pop("decision", None)
    st.session_state.pop("summary", None)
    st.info("Cleared a result from an earlier version. Run the analysis again.")


if "decision" in st.session_state and st.session_state["decision"]:
    d = st.session_state["decision"]

    color = COLORS[d["decision"]]
    label = LABELS[d["decision"]]

    st.markdown(f"### Decision: :{color}[{label}]")
    st.progress(d["confidence"] / 100, text=f"Confidence: {d['confidence']}%")

    st.subheader("💬 Summary")
    if st.session_state.get("summary"):
        st.write(st.session_state["summary"])
    else:
        st.session_state["summary"] = st.write_stream(
            stream_decision_summary(d)
        )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Matched skills")
        for skill in d["matched_skills"]:
            st.write(f"- {skill}")
    with col2:
        st.subheader("❌ Missing skills")
        for skill in d["missing_skills"]:
            st.write(f"- {skill}")

    st.subheader("📋 Breakdown")
    for r in d["reasoning"]:
        st.markdown(f"**{r['criterion']}** — {r['verdict']}")
        st.caption(f"Evidence: {r['source']}")
