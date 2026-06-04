# ===== RESUME ANALYZER =====

# ---- IMPORTS ----
import re
import os
import json
import time
import fitz
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ---- CONSTANTS ----
MODEL_NAME = "llama-3.3-70b-versatile"
MAX_TOKENS = 1000
TEMPERATURE = 0.1
MAX_RETRIES = 3
MIN_RECOMMENDED_SCORE = 60
MAX_TEXT_CHARS = 8000

# ---- DAY 1 & 2 — Basic Python ----
name = "Resume Analyzer"
print(f"Welcome to {name}")

def greet_user(name):
    print(f"Hello {name}, let's analyze your resume!")

skills = ["Python", "SQL", "Machine Learning"]
person = {"name": "John", "experience": 2}

greet_user("Your Name")
print(skills)
print(person)

# ---- DAY 3 — File Reading ----
def read_file(filepath):
    try:
        with open(filepath, "r") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Error: File Not Found!"

print(read_file("sample_resume.txt"))

# ---- DAY 4 — OOP & Error Handling ----
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

analyzer = ResumeAnalyzer("sample_resume.txt")
analyzer.load()
analyzer.display()

bad = ResumeAnalyzer("fake_file.txt")
bad.load()

# ---- DAY 5 — Groq AI API ----
def talk_to(message):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

print(talk_to("Hello! I am a CS student building an AI Resume Analyzer. Say hello back in one sentence!"))

# ---- DAY 6 & 10 — Text Cleaning ----
def clean_text(text):
    text = text.replace('\xa0', ' ')
    text = text.replace('\u2022', '-')
    text = text.replace('\uf0b7', '-')
    text = text.replace('\t', ' ')
    text = re.sub(r' +', ' ', text)
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    return '\n'.join(lines)

# ---- DAY 15 — Text Truncation ----
def truncate_text(text, max_chars=MAX_TEXT_CHARS):
    if len(text) > max_chars:
        return text[:max_chars] + "\n...[text truncated]"
    return text

# ---- DAY 7 — Week 1 Summary ----
print("\n===== RESUME ANALYZER =====")
print("Week 1 complete! Here's what this project can do:")
print("✅ Read resume files")
print("✅ Clean extracted text")
print("✅ Talk to AI")
print("============================\n")

# ---- DAY 9 — PDF Text Extraction ----
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

# ---- DAY 10 — Test Cleaning ----
print("\n--- Text Cleaning Test ---")
pdf_text = extract_text_from_pdf("test_resume.pdf")
cleaned = clean_text(pdf_text)
print(f"Original length: {len(pdf_text)} characters")
print(f"Cleaned length: {len(cleaned)} characters")
print("\nCleaned text preview (first 300 chars):")
print(cleaned[:300])

# ---- DAY 11 — Basic AI Analysis ----
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
            model=MODEL_NAME,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
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

# ---- DAY 12 — Improved Prompt Engineering ----
def clean_json_response(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def validate_response(data):
    required_keys = ["match_score", "top_strengths", "skill_gaps", "recommendation"]
    for key in required_keys:
        if key not in data:
            return False, f"Missing key: {key}"
    if not isinstance(data["match_score"], (int, float)):
        return False, "match_score must be a number"
    if not isinstance(data["top_strengths"], list):
        return False, "top_strengths must be a list"
    if not isinstance(data["skill_gaps"], list):
        return False, "skill_gaps must be a list"
    if not isinstance(data["recommendation"], str):
        return False, "recommendation must be a string"
    return True, "Valid"


def analyze_resume_v2(resume_text, job_description, max_retries=MAX_RETRIES):
    for attempt in range(max_retries):
        try:
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))

            system_prompt = """You are a Senior Technical Recruiter at a top tech company 
with 10 years of experience hiring software engineers.
You are known for accurate, fair, and detailed resume evaluations.
Always return valid JSON only. Never add markdown or explanations."""

            user_prompt = f"""Analyze this resume against the job description step by step.

Step 1: Identify all technical skills in the resume.
Step 2: Identify all required skills in the job description.
Step 3: Compare the two lists and find matches and gaps.
Step 4: Calculate a match percentage based on skill overlap.
Step 5: Return your analysis as JSON.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY a JSON object in exactly this format:
{{
    "match_score": 75,
    "top_strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "skill_gaps": ["Gap 1", "Gap 2", "Gap 3"],
    "recommendation": "One sentence recommendation here."
}}

Rules:
- match_score must be an integer between 0 and 100
- top_strengths must have EXACTLY 3 items
- skill_gaps must have EXACTLY 3 items
- each item must be 1-4 words maximum
- recommendation must be ONE sentence only
- Return ONLY the JSON, no markdown, no explanation"""

            response = client.chat.completions.create(
                model=MODEL_NAME,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            ai_text = response.choices[0].message.content
            cleaned = clean_json_response(ai_text)
            data = json.loads(cleaned)

            is_valid, message = validate_response(data)
            if is_valid:
                return data
            else:
                print(f"Attempt {attempt + 1} failed validation: {message}")

        except json.JSONDecodeError:
            print(f"Attempt {attempt + 1} failed: invalid JSON")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")

    return {"error": "Failed after 3 attempts"}

# ---- DAY 13 — Full Pipeline ----
def process_resume(pdf_path, job_description):
    if not pdf_path:
        return {"error": "No PDF path provided"}
    if not job_description:
        return {"error": "No job description provided"}
    if not pdf_path.endswith(".pdf"):
        return {"error": "File must be a PDF"}

    pdf_text = extract_text_from_pdf(pdf_path)
    if "Error" in pdf_text:
        return {"error": pdf_text}

    cleaned = truncate_text(clean_text(pdf_text))
    if not cleaned:
        return {"error": "No text could be extracted from PDF"}

    result = analyze_resume_v2(cleaned, job_description)
    return result


def print_result(result):
    print("=" * 50)
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Match Score    : {result['match_score']}%")
        print(f"Top Strengths  : {result['top_strengths']}")
        print(f"Skill Gaps     : {result['skill_gaps']}")
        print(f"Recommendation : {result['recommendation']}")
    print("=" * 50)

# ---- DAY 14 — Parse and Structure Results ----
def parse_analysis(result):
    score = result.get("match_score", 0)
    strengths = result.get("top_strengths", [])
    gaps = result.get("skill_gaps", [])
    recommendation = result.get("recommendation", "No recommendation available")

    try:
        score = int(score)
    except (ValueError, TypeError):
        score = 0

    if score >= 80:
        level = "Excellent"
    elif score >= 60:
        level = "Good"
    elif score >= 40:
        level = "Partial"
    else:
        level = "Poor"

    return {
        "score": score,
        "level": level,
        "strengths": strengths,
        "gaps": gaps,
        "recommendation": recommendation,
        "is_recommended": score >= MIN_RECOMMENDED_SCORE
    }


def display_analysis(parsed):
    print("\n" + "=" * 52)
    print("RESUME ANALYSIS REPORT".center(52))
    print("=" * 52)
    print(f"\n📊 Match Score : {parsed['score']}% — {parsed['level']} Match")
    print("\n✅ TOP STRENGTHS:")
    for i, s in enumerate(parsed['strengths'], 1):
        print(f"   {i}. {s}")
    print("\n❌ SKILL GAPS:")
    for i, g in enumerate(parsed['gaps'], 1):
        print(f"   {i}. {g}")
    print(f"\n💡 RECOMMENDATION:")
    print(f"   {parsed['recommendation']}")
    print("\n" + "-" * 52)
    if parsed['is_recommended']:
        print("🎯 VERDICT: RECOMMENDED FOR INTERVIEW ✅".center(52))
    else:
        print("🎯 VERDICT: NOT RECOMMENDED AT THIS TIME ❌".center(52))
    print("=" * 52 + "\n")

# ---- DAY 15 — Stress Test Suite ----
def run_stress_tests():
    print("\n" + "=" * 52)
    print("STRESS TEST SUITE".center(52))
    print("=" * 52)

    job_desc_python = """
    We are looking for a Software Engineer with:
    - 2+ years Python experience
    - REST APIs experience
    - SQL database knowledge
    """

    job_desc_security = """
    We are looking for a Cybersecurity Analyst with:
    - Network security experience
    - IBM certifications
    - Risk management skills
    """

    tests = [
        ("test_resume.pdf", job_desc_python, "Valid PDF + Python job"),
        ("test_resume.pdf", job_desc_security, "Valid PDF + Security job"),
        ("fake.pdf", job_desc_python, "Wrong PDF path"),
        ("test_resume.pdf", "", "Empty job description"),
        ("sample_resume.txt", job_desc_python, "Wrong file type"),
        ("test_resume.pdf", "Python developer needed", "Very short job desc"),
    ]

    results = []

    for pdf, job, label in tests:
        result = process_resume(pdf, job)
        if "error" in result:
            status = "❌ ERROR"
            detail = result["error"]
        else:
            parsed = parse_analysis(result)
            status = "✅ PASS"
            detail = f"Score: {parsed['score']}% — {parsed['level']}"
        results.append((label, status, detail))

    print("\nTest Results:")
    print("-" * 52)
    for label, status, detail in results:
        print(f"{status} | {label}")
        print(f"       {detail}")
        print("-" * 52)

    passed = sum(1 for _, s, _ in results if "PASS" in s)
    total = len(results)
    print(f"\nSummary: {passed}/{total} tests produced valid analysis")
    print("=" * 52)


run_stress_tests()