# streamlit_app.py

import streamlit as st
from io import BytesIO
import sys
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.utils.extract_text_pdf import extract_text_from_pdf  # type: ignore  # noqa: E402
from app.services.llm import generate_response  # type: ignore  # noqa: E402

st.set_page_config(
    page_title="Resume-JD Match Analyzer",
    page_icon="🧠",
    layout="wide",
)

st.title("📄 Resume vs JD Match Analyzer")
st.caption("Run fully inside Streamlit • FastAPI optional • JD as text or PDF")

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

# Internal processing (no HTTP calls)
if analyze_clicked:
    # Validate inputs
    if not resume_file:
        st.error("Please upload your resume (PDF).")
    elif jd_mode == "Paste text" and not (jd_text and jd_text.strip()):
        st.error("Please paste the JD text or switch to PDF upload.")
    elif jd_mode == "Upload PDF" and not jd_file:
        st.error("Please upload the JD PDF or switch to text input.")
    else:
        with st.spinner("Evaluating with AI..."):
            try:
                # Extract resume text
                resume_bytes = BytesIO(resume_file.getvalue())
                resume_content = extract_text_from_pdf(resume_bytes)

                # Extract or use JD text
                if jd_mode == "Upload PDF" and jd_file is not None:
                    jd_bytes = BytesIO(jd_file.getvalue())
                    jd_content = extract_text_from_pdf(jd_bytes)
                else:
                    jd_content = (jd_text or "").strip()

                # Run LLM-based comparison
                data = generate_response(jd_content, resume_content)

                with result_container:
                    if "error" in data:
                        st.error(f"LLM error: {data.get('detail', 'Unknown error')}")
                        if data.get("raw_response"):
                            with st.expander("Raw response"):
                                st.code(data["raw_response"], language="json")
                    else:
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

            except Exception as e:
                st.error(f"Unexpected error: {e}")

if not analyze_clicked:
    with right:
        st.info("Upload your resume and provide the JD to get a match analysis.")
