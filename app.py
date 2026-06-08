import streamlit as st
import tempfile
import os
import sys
import datetime

sys.path.append(os.path.dirname(__file__))
from main import process_resume, parse_analysis

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

if "result" not in st.session_state:
    st.session_state.result = None
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "parsed" not in st.session_state:
    st.session_state.parsed = None
if "analysis_time" not in st.session_state:
    st.session_state.analysis_time = None
if "error_msg" not in st.session_state:
    st.session_state.error_msg = None


def clear_results():
    st.session_state.result = None
    st.session_state.parsed = None
    st.session_state.analyzed = False
    st.session_state.analysis_time = None
    st.session_state.error_msg = None


def is_valid_pdf(file_bytes):
    return file_bytes[:4] == b'%PDF'


def run_analysis(file_bytes, job_desc):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        result = process_resume(tmp_path, job_desc)
        return result, None

    except Exception as e:
        return None, str(e)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


with st.sidebar:
    st.header("📖 How to use")
    st.write("1. Upload your resume as PDF")
    st.write("2. Paste the job description")
    st.write("3. Click Analyze Resume")
    st.divider()
    st.info("Powered by Groq AI + LLaMA 3.3")
    st.divider()
    with st.expander("ℹ️ About this tool"):
        st.write("This tool uses AI to compare your resume against a job description and gives you a match score, strengths, skill gaps, and a recommendation.")

st.title("📄 AI Resume Analyzer")
st.write("Upload your resume and get instant AI-powered feedback.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume")
    uploaded_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"],
        on_change=clear_results
    )

    if uploaded_file is None:
        st.info("👆 Upload your resume PDF to begin")
    else:
        file_bytes = uploaded_file.getvalue()

        if not is_valid_pdf(file_bytes):
            st.error("❌ This file is not a valid PDF. Please upload a proper PDF file.")
            st.stop()

        size = uploaded_file.size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"

        st.success(f"✅ {uploaded_file.name}")
        st.caption(f"File size: {size_str}")

with col2:
    st.subheader("💼 Job Description")
    job_desc = st.text_area(
        "Paste the job description here",
        height=200,
        placeholder="We are looking for a Python developer with 2+ years experience in REST APIs and SQL...",
        on_change=clear_results
    )

    char_count = len(job_desc) if job_desc else 0

    if char_count == 0:
        st.caption("Paste the job description you are applying for")
    elif char_count < 50:
        st.warning(f"⚠️ {char_count} characters — add more detail for better analysis")
    else:
        st.caption(f"✅ {char_count} characters")

st.divider()

ready = uploaded_file is not None and char_count >= 50
analyze_btn = st.button("✨ Analyze Resume", disabled=not ready)

if not ready:
    if uploaded_file is None and char_count < 50:
        st.caption("Upload a PDF and paste a job description to enable analysis")
    elif uploaded_file is None:
        st.caption("Upload a PDF resume to enable analysis")
    else:
        st.caption("Add more detail to the job description to enable analysis")

if analyze_btn and ready:
    st.session_state.error_msg = None

    with st.status("Analyzing your resume...", expanded=True) as status:
        st.write("📄 Validating PDF...")
        file_bytes = uploaded_file.getvalue()

        if not is_valid_pdf(file_bytes):
            status.update(label="❌ Invalid PDF", state="error")
            st.session_state.error_msg = "This file is not a valid PDF."
        else:
            st.write("🧹 Processing resume text...")
            st.write("🤖 Getting AI analysis...")

            result, error = run_analysis(file_bytes, job_desc)

            if error:
                status.update(label="❌ Analysis failed", state="error")
                st.session_state.error_msg = error
            elif "error" in result:
                error_msg = result["error"]
                status.update(label="❌ Analysis failed", state="error")

                if "not found" in error_msg.lower():
                    st.session_state.error_msg = "Could not read the PDF. Please try uploading again."
                elif "image only" in error_msg.lower():
                    st.session_state.error_msg = "This PDF contains only images. Please upload a text-based PDF."
                elif "rate limit" in error_msg.lower():
                    st.session_state.error_msg = "AI service is busy. Please wait 30 seconds and try again."
                else:
                    st.session_state.error_msg = error_msg
            else:
                st.session_state.result = result
                st.session_state.parsed = parse_analysis(result)
                st.session_state.analyzed = True
                st.session_state.analysis_time = datetime.datetime.now()
                status.update(
                    label="✅ Analysis complete!",
                    state="complete",
                    expanded=False
                )

if st.session_state.error_msg:
    st.error(f"❌ {st.session_state.error_msg}")

if st.session_state.analyzed and st.session_state.parsed:
    parsed = st.session_state.parsed

    if st.session_state.analysis_time:
        time_str = st.session_state.analysis_time.strftime("%I:%M %p")
        st.caption(f"Analysis performed at {time_str}")

    st.divider()
    st.header("📊 Analysis Results")

    col3, col4, col5 = st.columns(3)

    with col3:
        st.metric("Match Score", f"{parsed['score']}%")

    with col4:
        st.metric("Match Level", parsed['level'])

    with col5:
        verdict = "✅ Recommended" if parsed['is_recommended'] else "❌ Not Recommended"
        st.metric("Verdict", verdict)

    st.progress(parsed['score'] / 100)
    st.divider()

    col6, col7 = st.columns(2)

    with col6:
        st.subheader("✅ Top Strengths")
        for i, s in enumerate(parsed['strengths'], 1):
            st.success(f"{i}. {s}")

    with col7:
        st.subheader("❌ Skill Gaps")
        for i, g in enumerate(parsed['gaps'], 1):
            st.warning(f"{i}. {g}")

    st.divider()
    st.subheader("💡 Recommendation")
    st.info(parsed['recommendation'])

    st.divider()
    if st.button("🔄 Analyze Another Resume"):
        clear_results()
        st.rerun()