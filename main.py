# ===== RESUME ANALYZER =====
# Week 1 Complete

# ---- IMPORTS (all at top) ----
import re
import os
import json
import fitz
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

name = "Resume Analyzer"
print(f"Welcome to {name}")

def greet_user(name):
    print(f"Hello {name}, let's analyze your resume!")

skills = ["Python", "SQL", "Machine Learning"]
person = {"name": "John", "experience": 2}

greet_user("Your Name")
print(skills)
print(person)

#File Reading 
def read_file(filepath):
    try:
        with open(filepath, "r") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Error: File Not Found!"

result=read_file("sample_resume.txt")
print(result)

#OOP & Error Handling ----
class ResumeAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.content = None

    def load(self):
        try:
            with open(self.filepath, "r") as f:
                self.content = f.read()
            print("Resume loaded successfully!")
        except FileNotFoundError:
            print("Error: Resume file not found!")
        except Exception as e:
            print(f"Something went wrong: {e}")

    def display(self):
        if self.content:
            print(self.content)
        else:
            print("No resume loaded yet!")

analyzer=ResumeAnalyzer("sample_resume.txt")
analyzer.load()
analyzer.display()

bad=ResumeAnalyzer("fake_file.txt")
bad.load()

#Groq AI API 
def talk_to(message):
    try:
        client=Groq(api_key=os.getenv("GROQ_API_KEY"))
        response=client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

result=talk_to("Hello! I am a CS student building an AI Resume Analyzer. Say hello back in one sentence!")
print(result)

def clean_text(text):
    # Handle special PDF characters
    text = text.replace('\xa0', ' ')
    text = text.replace('\u2022', '-')
    text = text.replace('\uf0b7', '-')
    text = text.replace('\t', ' ')
    
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Clean line by line
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    
    return '\n'.join(lines)
#PDF text extraction
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        if not full_text.strip():
            return "No text found — PDF may be image only"
        return full_text
    except FileNotFoundError:
        return "Error: PDF file not found"
    except Exception as e:
        return f"Error: {e}"

# DAY 11 — AI Resume Analysis
def analyze_resume(resume_text, job_description):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        system_prompt = """You are an expert resume analyzer with 10 years 
of experience hiring for tech companies.
Analyze resumes professionally and return structured JSON only."""

        user_prompt = f"""Analyze this resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY a JSON object with exactly these fields:
- match_score: number from 0 to 100
- top_strengths: list of exactly 3 strings
- skill_gaps: list of exactly 3 strings
- recommendation: one sentence string

Return ONLY the JSON. No explanation. No markdown. No extra text."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1000,
            temperature=0.1,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        ai_text = response.choices[0].message.content
        data = json.loads(ai_text)
        return data

    except json.JSONDecodeError:
        return {"error": "AI returned invalid JSON"}
    except Exception as e:
        return {"error": str(e)}

# Test it
pdf_text = extract_text_from_pdf("test_resume.pdf")
cleaned = clean_text(pdf_text)
print("Extracted and cleaned PDF text:")
print(cleaned)
raw_text=read_file("sample_resume.txt")
cleaned=clean_text(raw_text)
print("Cleaned resume:")
print(cleaned)


print("\n===== RESUME ANALYZER =====")
print("Week 1 complete! Here's what this project can do:")
print("✅ Read resume files")
print("✅ Clean extracted text")
print("✅ Talk to AI")
print("============================\n")


print("\n---Improved Text Cleaning ---")

# Test with real PDF
pdf_text = extract_text_from_pdf("test_resume.pdf")
cleaned = clean_text(pdf_text)

print(f"Original length: {len(pdf_text)} characters")
print(f"Cleaned length: {len(cleaned)} characters")
print("\nCleaned text preview (first 300 chars):")
print(cleaned[:300])

# Test resume analysis
print("\n--- AI Resume Analysis ---")

pdf_text = extract_text_from_pdf("test_resume.pdf")
cleaned = clean_text(pdf_text)

job_description = """
We are looking for a Software Engineer with:
- 2+ years of Python experience
- Experience with REST APIs
- SQL database knowledge
- Problem solving skills
- Good communication
"""

result = analyze_resume(cleaned, job_description)

if "error" in result:
    print(f"Error: {result['error']}")
else:
    print(f"Match Score: {result['match_score']}%")
    print(f"Top Strengths: {result['top_strengths']}")
    print(f"Skill Gaps: {result['skill_gaps']}")
    print(f"Recommendation: {result['recommendation']}")