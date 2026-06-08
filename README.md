# 📄 AI Resume Analyzer

An AI-powered resume analyzer built with Python, Groq AI, and Streamlit.

## 🔗 Live Demo
[Click here to try it live](YOUR_STREAMLIT_URL_HERE)

## What it does
- Upload your resume as a PDF
- Paste any job description
- Get instant AI analysis:
  - Match score (0-100%)
  - Top 3 strengths
  - Top 3 skill gaps
  - Specific improvement suggestions
  - Recommendation verdict
  - Download full report as PDF

## Tech Stack
- Python
- Groq API (LLaMA 3.3 70B)
- PyMuPDF (PDF parsing)
- Streamlit (web app)
- ReportLab (PDF generation)

## How to run locally
1. Clone the repo
   git clone https://github.com/Krishn2607/resume-analyzer.git
2. Install requirements
   pip install -r requirements.txt
3. Create .env file and add your Groq API key
   GROQ_API_KEY=your_key_here
4. Run the app
   streamlit run app.py

## Built by
Krishn Karelia — CE Student
