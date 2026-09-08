import streamlit as st
from tools.analyzer import analyze_job
from tools.analyzer import stream_decision_summary

st.set_page_config(page_title="Job Match Advisor", page_icon="💼")
st.title("💼 Job Match Advisor")
st.write("Paste the job posting, and I’ll analyze it and compare it with your CV.")

job_text = st.text_area(
    label="Job Description",
    height=300,
    placeholder="Paste the job description here...",
)

analyze_clicked = st.button("Analyze Job", type="primary")


if analyze_clicked and job_text.strip():
    with st.status("Analyzing the job...", expanded=True) as status:
        st.write("📄 Extracting job requirements...")
        st.write("🔍 Looking for evidence in the CV...")
        st.write("⚖️ Making the decision...")

        decision = analyze_job(job_text)
        status.update(label="Analysis complete ✅", state="complete", expanded=False)

    if decision is None:
        st.error("مرجعش قرار منظّم من Claude. جرّب تاني.")
    else:
        st.session_state["decision"] = decision
        st.session_state["summary"] = None


if "decision" in st.session_state and st.session_state["decision"]:
    d = st.session_state["decision"]

    colors = {"قدم": "green", "قدم_بحذر": "orange", "لا_تقدم": "red"}
    color = colors.get(d["decision"], "gray")

    st.markdown(f"### القرار: :{color}[{d['decision']}]")
    st.progress(d["confidence"] / 100, text=f"الثقة: {d['confidence']}%")

    st.subheader("💬 الخلاصة")
    if st.session_state.get("summary"):
        st.write(st.session_state["summary"])  # محفوظ → اعرضه ببلاش
    else:
        st.session_state["summary"] = st.write_stream(  # مش محفوظ → ابثّه واحفظه
            stream_decision_summary(d)
        )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ مهارات متطابقة")
        for skill in d["matched_skills"]:
            st.write(f"- {skill}")
    with col2:
        st.subheader("❌ مهارات ناقصة")
        for skill in d["missing_skills"]:
            st.write(f"- {skill}")

    st.subheader("📋 التفصيل")
    for r in d["reasoning"]:
        st.markdown(f"**{r['criterion']}** — {r['verdict']}")
        st.caption(f"الدليل: {r['source']}")