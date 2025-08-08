# streamlit_app.py

import streamlit as st
import requests
from io import BytesIO

API_URL = "http://localhost:8000/analyze"

st.set_page_config(
    page_title="Resume-JD Match Analyzer",
    page_icon="🧠",
    layout="wide",
)

st.title("📄 Resume vs JD Match Analyzer")
st.caption("FastAPI + Gemini | Upload resume PDF and provide JD as text or PDF")

# Layout
left, right = st.columns([1, 1])

with left:
    st.subheader("Inputs")
    resume_file = st.file_uploader("Resume (PDF)", type=["pdf"], help="Required")

    jd_mode = st.radio(
        "Job Description source",
        options=["Paste text", "Upload PDF"],
        horizontal=True,
    )

    jd_text = None
    jd_file = None

    if jd_mode == "Paste text":
        jd_text = st.text_area(
            "Paste JD text",
            placeholder="Paste the job description here...",
            height=220,
        )
        st.caption(
            f"Characters: {len(jd_text or '')} | Tip: You can also upload a PDF instead."
        )
    else:
        jd_file = st.file_uploader("JD (PDF)", type=["pdf"], key="jd_pdf")

    analyze_clicked = st.button("🚀 Analyze Match", type="primary", use_container_width=True)

with right:
    st.subheader("Result")
    result_container = st.container()

# Submit to API
if analyze_clicked:
    if not resume_file:
        st.error("Please upload your resume (PDF).")
    elif jd_mode == "Paste text" and not (jd_text and jd_text.strip()):
        st.error("Please paste the JD text or switch to PDF upload.")
    elif jd_mode == "Upload PDF" and not jd_file:
        st.error("Please upload the JD PDF or switch to text input.")
    else:
        with st.spinner("Evaluating with AI..."):
            try:
                files = {
                    "resume_file": (resume_file.name, resume_file, "application/pdf"),
                }
                data = {}

                if jd_mode == "Upload PDF" and jd_file is not None:
                    files["jd_file"] = (jd_file.name, jd_file, "application/pdf")
                else:
                    data["jd_text"] = jd_text

                response = requests.post(API_URL, files=files, data=data, timeout=120)
                response.raise_for_status()
                data = response.json()

                with result_container:
                    score = data.get("match_score")
                    if isinstance(score, (int, float)):
                        st.metric("Match Score", f"{score}%")
                        st.progress(min(max(int(score), 0), 100) / 100.0)

                    cols = st.columns(2)
                    with cols[0]:
                        st.markdown("### 🟢 Strengths")
                        strengths = data.get("strengths", [])
                        if strengths:
                            for s in strengths:
                                st.markdown(f"- {s}")
                        else:
                            st.info("No strengths identified.")
                    with cols[1]:
                        st.markdown("### 🔴 Missing Skills")
                        missing = data.get("missing_skills", [])
                        if missing:
                            for m in missing:
                                st.markdown(f"- {m}")
                        else:
                            st.success("No major gaps detected.")

                    st.markdown("### 💡 Recommendation")
                    st.write(data.get("recommendation", "N/A"))

                    if data.get("summary"):
                        with st.expander("Summary"):
                            st.write(data["summary"])

            except requests.exceptions.RequestException as e:
                st.error(f"API error: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

if not analyze_clicked:
    with right:
        st.info("Upload your resume and provide the JD to get a match analysis.")
