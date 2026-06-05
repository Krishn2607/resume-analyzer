import streamlit as st
import tempfile
import os
import sys

sys.path.append(os.path.dirname(__file__))
from main import process_resume, parse_analysis

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

with st.sidebar:
    st.header("📖 How to use")
    st.write("1. Upload your resume as PDF")
    st.write("2. Paste the job description")
    st.write("3. Click Analyze Resume")
    st.divider()
    st.info("Powered by Groq AI + LLaMA 3.3")

st.title("📄 AI Resume Analyzer")
st.write("Upload your resume and get instant AI-powered feedback.")
st.divider()

st.header("Upload & Analyze")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
job_desc = st.text_area("Paste Job Description here", height=150, placeholder="We are looking for a Python developer with 2+ years experience...")

analyze_btn = st.button("✨ Analyze Resume")

if analyze_btn:
    if not uploaded_file:
        st.error("❌ Please upload a PDF resume first")
    elif not job_desc:
        st.error("❌ Please paste a job description")
    else:
        with st.spinner("Analyzing your resume with AI..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            result = process_resume(tmp_path, job_desc)
            os.unlink(tmp_path)

        if "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            parsed = parse_analysis(result)

            st.divider()
            st.header("📊 Analysis Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Match Score", f"{parsed['score']}%")

            with col2:
                st.metric("Match Level", parsed['level'])

            with col3:
                verdict = "✅ Recommended" if parsed['is_recommended'] else "❌ Not Recommended"
                st.metric("Verdict", verdict)

            st.divider()

            col4, col5 = st.columns(2)

            with col4:
                st.subheader("✅ Top Strengths")
                for i, s in enumerate(parsed['strengths'], 1):
                    st.success(f"{i}. {s}")

            with col5:
                st.subheader("❌ Skill Gaps")
                for i, g in enumerate(parsed['gaps'], 1):
                    st.warning(f"{i}. {g}")

            st.divider()
            st.subheader("💡 Recommendation")
            st.info(parsed['recommendation'])