import streamlit as st
import tempfile
import os
import sys
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from io import BytesIO

sys.path.append(os.path.dirname(__file__))
from main import process_resume, parse_analysis

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #0a0a0f; }
    .stButton > button {
        background-color: #6c63ff;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover { background-color: #5a52e0; }
    .stButton > button:disabled {
        background-color: #2a2a3e;
        color: #555;
    }
    .stTextArea textarea {
        background-color: #111118;
        border: 1px solid #222233;
        color: #e8e8f0;
    }
    .stSidebar { background-color: #080810; }
    div[data-testid="stFileUploader"] {
        background-color: #111118;
        border-radius: 8px;
        padding: 8px;
    }
    </style>
""", unsafe_allow_html=True)

MAX_FILE_SIZE_MB = 5
MIN_JOB_DESC_CHARS = 50
MIN_EXTRACTED_CHARS = 100

ERROR_MESSAGES = {
    "not found": "Could not find the PDF file. Please upload again.",
    "image only": "This PDF contains only scanned images. Please upload a text-based PDF.",
    "rate_limit": "AI service is busy. Please wait 30 seconds and try again.",
    "rate limit": "AI service is busy. Please wait 30 seconds and try again.",
    "connection": "Internet connection issue. Please check your connection and retry.",
    "timeout": "Request timed out. Please try again.",
    "invalid json": "AI returned an unexpected response. Please try again.",
    "failed after 3": "Analysis failed after multiple attempts. Please try again later.",
    "no text": "Could not extract text from this PDF.",
    "token": "Resume is too long. Please try a shorter resume.",
    "password": "This PDF is password protected. Please remove the password first.",
}

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
if "total_analyses" not in st.session_state:
    st.session_state.total_analyses = 0
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "textarea_key" not in st.session_state:
    st.session_state.textarea_key = 0


def clear_results():
    st.session_state.result = None
    st.session_state.parsed = None
    st.session_state.analyzed = False
    st.session_state.analysis_time = None
    st.session_state.error_msg = None
    st.session_state.uploader_key += 1
    st.session_state.textarea_key += 1


def get_friendly_error(error_msg):
    error_lower = error_msg.lower()
    for keyword, friendly_msg in ERROR_MESSAGES.items():
        if keyword in error_lower:
            return friendly_msg
    return f"Something went wrong: {error_msg}"


def is_valid_pdf(file_bytes):
    return file_bytes[:4] == b'%PDF'


def sanitize_job_desc(text):
    if not text:
        return ""
    text = " ".join(text.split())
    if len(text) > 5000:
        text = text[:5000]
    return text.strip()


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


def get_score_color(score):
    if score >= 80:
        return "#6bcb77"
    elif score >= 60:
        return "#ffd93d"
    elif score >= 40:
        return "#ff9a3c"
    else:
        return "#ff6b6b"


def render_score_card(parsed):
    score = parsed['score']
    level = parsed['level']
    color = get_score_color(score)

    st.markdown(f"""
        <div style="
            background: {color}15;
            border: 1px solid {color};
            border-radius: 16px;
            padding: 28px;
            text-align: center;
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 13px; color: #888; letter-spacing: 0.1em; margin-bottom: 8px;">
                MATCH SCORE
            </div>
            <div style="font-size: 52px; font-weight: 800; color: {color}; line-height: 1;">
                {score}%
            </div>
            <div style="font-size: 16px; color: {color}; margin-top: 10px; opacity: 0.85;">
                {level} Match
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_strengths(strengths):
    for s in strengths:
        st.markdown(f"""
            <div style="
                background: #6bcb7712;
                border: 1px solid #6bcb7740;
                border-left: 3px solid #6bcb77;
                border-radius: 8px;
                padding: 10px 14px;
                margin-bottom: 8px;
                color: #d0f0d8;
                font-size: 14px;
            ">✅ {s}</div>
        """, unsafe_allow_html=True)


def render_gaps(gaps):
    for g in gaps:
        st.markdown(f"""
            <div style="
                background: #ff6b6b12;
                border: 1px solid #ff6b6b40;
                border-left: 3px solid #ff6b6b;
                border-radius: 8px;
                padding: 10px 14px;
                margin-bottom: 8px;
                color: #f0d0d0;
                font-size: 14px;
            ">❌ {g}</div>
        """, unsafe_allow_html=True)
        
def render_improvements(improvements):
    for i, tip in enumerate(improvements, 1):
        st.markdown(f"""
            <div style="
                background: #1a1a3e12;
                border: 1px solid #6666ff40;
                border-left: 3px solid #6666ff;
                border-radius: 8px;
                padding: 10px 14px;
                margin-bottom: 8px;
                color: #ccccff;
                font-size: 14px;
            ">💡 {i}. {tip}</div>
        """, unsafe_allow_html=True)


def render_recommendation(text):
    st.markdown(f"""
        <div style="
            background: #1a1a3e;
            border: 1px solid #4444aa;
            border-left: 4px solid #6666ff;
            border-radius: 8px;
            padding: 16px 20px;
            color: #ccccff;
            font-size: 15px;
            line-height: 1.7;
            font-style: italic;
        ">💡 {text}</div>
    """, unsafe_allow_html=True)


def render_verdict(is_recommended, score):
    color = "#6bcb77" if is_recommended else "#ff6b6b"
    text = "🎯 RECOMMENDED FOR INTERVIEW ✅" if is_recommended else "❌ NOT RECOMMENDED AT THIS TIME"

    st.markdown(f"""
        <div style="
            background: {color}20;
            border: 1px solid {color};
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            font-size: 20px;
            font-weight: 700;
            color: {color};
            margin-top: 8px;
        ">{text}</div>
    """, unsafe_allow_html=True)

    if is_recommended and score >= 80:
        st.balloons()

def generate_pdf(parsed, job_desc_preview):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6
    )

    heading_style = ParagraphStyle(
        "heading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#6c63ff"),
        spaceBefore=14,
        spaceAfter=6
    )

    normal_style = ParagraphStyle(
        "normal",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#222222"),
        spaceAfter=5,
        leading=16
    )

    score_style = ParagraphStyle(
        "score",
        parent=styles["Normal"],
        fontSize=32,
        textColor=colors.HexColor("#6c63ff"),
        spaceAfter=4,
        fontName="Helvetica-Bold"
    )

    story = []

    story.append(Paragraph("AI Resume Analyzer", title_style))
    story.append(Paragraph("Resume Analysis Report", styles["Normal"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dddddd")))
    story.append(Spacer(1, 0.15 * inch))

    from datetime import datetime
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"Generated on: {now}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Match Score", heading_style))
    story.append(Paragraph(f"{parsed['score']}%", score_style))
    story.append(Paragraph(f"Level: {parsed['level']} Match", normal_style))
    story.append(Spacer(1, 0.1 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#eeeeee")))

    story.append(Paragraph("Top Strengths", heading_style))
    for i, s in enumerate(parsed['strengths'], 1):
        story.append(Paragraph(f"{i}. ✓ {s}", normal_style))

    story.append(Spacer(1, 0.1 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#eeeeee")))

    story.append(Paragraph("Skill Gaps", heading_style))
    for i, g in enumerate(parsed['gaps'], 1):
        story.append(Paragraph(f"{i}. {g}", normal_style))

    if parsed.get('improvements'):
        story.append(Spacer(1, 0.1 * inch))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#eeeeee")))
        story.append(Paragraph("How to Improve", heading_style))
        for i, tip in enumerate(parsed['improvements'], 1):
            story.append(Paragraph(f"{i}. {tip}", normal_style))

    story.append(Spacer(1, 0.1 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#eeeeee")))
    story.append(Paragraph("Recommendation", heading_style))
    story.append(Paragraph(parsed['recommendation'], normal_style))

    story.append(Spacer(1, 0.1 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#eeeeee")))
    story.append(Paragraph("Verdict", heading_style))
    verdict_text = "RECOMMENDED FOR INTERVIEW" if parsed['is_recommended'] else "NOT RECOMMENDED AT THIS TIME"
    verdict_color = colors.HexColor("#2e7d32") if parsed['is_recommended'] else colors.HexColor("#c62828")
    verdict_style = ParagraphStyle(
        "verdict",
        parent=styles["Normal"],
        fontSize=13,
        textColor=verdict_color,
        fontName="Helvetica-Bold",
        spaceAfter=6
    )
    story.append(Paragraph(verdict_text, verdict_style))

    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dddddd")))
    story.append(Spacer(1, 0.1 * inch))
    footer_style = ParagraphStyle(
        "footer",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#888888")
    )
    story.append(Paragraph("Generated by AI Resume Analyzer · Powered by Groq AI · LLaMA 3.3", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

def render_empty_state():
    st.markdown("""
        <div style="
            text-align: center;
            padding: 60px 20px;
            color: #444;
            border: 2px dashed #222;
            border-radius: 16px;
            margin-top: 20px;
        ">
            <div style="font-size: 48px;">📊</div>
            <div style="font-size: 18px; margin-top: 16px; color: #555;">
                Your analysis results will appear here
            </div>
            <div style="font-size: 14px; margin-top: 8px; color: #3a3a5a;">
                Upload a resume and paste a job description to get started
            </div>
        </div>
    """, unsafe_allow_html=True)


def display_results(parsed):
    st.markdown("---")
    st.header("📊 Analysis Results")
    st.write("")

    col1, col2, col3 = st.columns([1, 1.5, 1.5])

    with col1:
        render_score_card(parsed)

    with col2:
        st.subheader("✅ Top Strengths")
        render_strengths(parsed['strengths'])

    with col3:
        st.subheader("❌ Skill Gaps")
        render_gaps(parsed['gaps'])

    st.write("")
    st.markdown("---")
    st.subheader("🚀 How to Improve")
    st.write("")
    render_improvements(parsed.get('improvements', []))

    st.write("")
    st.markdown("---")
    st.subheader("💡 Recommendation")
    st.write("")
    render_recommendation(parsed['recommendation'])

    st.write("")
    render_verdict(parsed['is_recommended'], parsed['score'])
    st.markdown("---")

    pdf_buffer = generate_pdf(parsed, "")
    st.download_button(
        label="📥 Download Report as PDF",
        data=pdf_buffer,
        file_name="resume_analysis_report.pdf",
        mime="application/pdf"
    )


# ---- SIDEBAR ----
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0;">
            <div style="font-size: 32px;">📄</div>
            <div style="font-size: 16px; font-weight: 700; color: #e8e8f0;">
                🚀 ResumePilot AI
            </div>
            <div style="font-size: 12px; color: #555; margin-top: 4px;">
                AI-Powered Career Matching
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📖 How to use")
    st.write("1. Upload your resume as PDF")
    st.write("2. Paste the job description")
    st.write("3. Click Analyze Resume")

    st.divider()
    st.subheader("💡 Tips")
    st.write("✅ Use 100+ word job description")
    st.write("✅ PDF must have selectable text")
    st.write("✅ Include a skills section")
    st.write("✅ Max file size: 5 MB")

    st.divider()
    with st.expander("ℹ️ About"):
        st.write("This tool uses LLaMA 3.3 via Groq to analyze your resume against any job description.")
        st.write(f"Version 1.0")

    st.divider()
    st.caption(f"Analyses this session: {st.session_state.total_analyses}")

# ---- HERO ----
st.markdown("""
    <div style="
        text-align: center;
        padding: 40px 20px 30px;
        background: linear-gradient(135deg, #1a1a2e 0%, #0d0d1a 100%);
        border-radius: 16px;
        margin-bottom: 24px;
        border: 1px solid #222233;
    ">
        <div style="font-size: 42px; font-weight: 800; color: #ffffff; margin: 0;">
            📄 AI Resume Analyzer
        </div>
        <div style="color: #6868a0; font-size: 16px; margin-top: 12px;">
            Upload your resume · Paste a job description · Get instant AI feedback
        </div>
    </div>
""", unsafe_allow_html=True)

# ---- INPUTS ----
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📄 Your Resume")
    uploaded_file = st.file_uploader(
    "Upload Resume PDF",
    type=["pdf"],
    key=f"uploader_{st.session_state.uploader_key}"
)

    if uploaded_file is None:
        st.info("👆 Upload your resume PDF to begin")
    else:
        file_bytes = uploaded_file.getvalue()

        if not is_valid_pdf(file_bytes):
            st.error("❌ This file is not a valid PDF.")
            st.stop()

        size_mb = uploaded_file.size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            st.error(f"❌ File is too large ({size_mb:.1f} MB). Maximum size is {MAX_FILE_SIZE_MB} MB.")
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

with col_b:
    st.subheader("💼 Job Description")
    job_desc = st.text_area(
    "Paste the job description here",
    height=200,
    placeholder="We are looking for a Python developer with 2+ years experience in REST APIs and SQL...",
    key=f"textarea_{st.session_state.textarea_key}"
)

    char_count = len(job_desc) if job_desc else 0

    if char_count == 0:
        st.caption("Paste the job description you are applying for")
    elif char_count < MIN_JOB_DESC_CHARS:
        st.warning(f"⚠️ {char_count} characters — add more detail for better analysis")
    else:
        st.caption(f"✅ {char_count} characters")

st.divider()

ready = uploaded_file is not None and char_count >= MIN_JOB_DESC_CHARS
analyze_btn = st.button("✨ Analyze Resume", disabled=not ready)

if not ready:
    if uploaded_file is None and char_count < MIN_JOB_DESC_CHARS:
        st.caption("Upload a PDF and paste a job description to enable analysis")
    elif uploaded_file is None:
        st.caption("Upload a PDF resume to enable analysis")
    else:
        st.caption("Add more detail to the job description to enable analysis")

# ---- ANALYSIS ----
if analyze_btn and ready:
    st.session_state.error_msg = None
    clean_job = sanitize_job_desc(job_desc)

    with st.status("Analyzing your resume...", expanded=True) as status:
        st.write("📄 Validating PDF...")
        file_bytes = uploaded_file.getvalue()

        if not is_valid_pdf(file_bytes):
            status.update(label="❌ Invalid PDF", state="error")
            st.session_state.error_msg = "This file is not a valid PDF."
        else:
            st.write("🧹 Processing resume text...")
            st.write("🤖 Getting AI analysis...")

            result, error = run_analysis(file_bytes, clean_job)

            if error:
                status.update(label="❌ Analysis failed", state="error")
                st.session_state.error_msg = get_friendly_error(error)
            elif result is None:
                status.update(label="❌ Analysis failed", state="error")
                st.session_state.error_msg = "Analysis returned no result. Please try again."
            elif "error" in result:
                status.update(label="❌ Analysis failed", state="error")
                st.session_state.error_msg = get_friendly_error(result["error"])
            else:
                st.session_state.result = result
                st.session_state.parsed = parse_analysis(result)
                st.session_state.analyzed = True
                st.session_state.analysis_time = datetime.datetime.now()
                st.session_state.total_analyses += 1
                status.update(
                    label="✅ Analysis complete!",
                    state="complete",
                    expanded=False
                )
                st.toast("Analysis complete! 🎉", icon="✅")

if st.session_state.error_msg:
    st.error(f"❌ {st.session_state.error_msg}")

# ---- RESULTS ----
if st.session_state.analyzed and st.session_state.parsed:
    parsed = st.session_state.parsed

    if st.session_state.analysis_time:
        time_str = st.session_state.analysis_time.strftime("%I:%M %p")
        st.caption(f"Analysis performed at {time_str}")

    display_results(parsed)

    if st.button("🔄 Analyze Another Resume"):
        clear_results()
        st.rerun()
else:
    render_empty_state()

# ---- FOOTER ----
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #333; font-size: 12px; padding: 16px;">
        Built with Python · Groq AI · LLaMA 3.3 · Streamlit
        &nbsp;·&nbsp; Resume Analyzer v1.0
    </div>
""", unsafe_allow_html=True)