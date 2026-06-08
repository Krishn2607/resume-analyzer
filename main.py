# ===== RESUME ANALYZER =====

# ---- IMPORTS ----
import re
import os
import json
import fitz
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ---- CONSTANTS ----
MODEL_NAME = "llama-3.3-70b-versatile"
MAX_TOKENS = 1000
TEMPERATURE = 0.1
MAX_RETRIES = 3
MIN_RECOMMENDED_SCORE = 80
MAX_TEXT_CHARS = 8000


# ---- TEXT CLEANING ----
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


# ---- TEXT TRUNCATION ----
def truncate_text(text, max_chars=MAX_TEXT_CHARS):
    if len(text) > max_chars:
        return text[:max_chars] + "\n...[text truncated]"
    return text


# ---- PDF TEXT EXTRACTION ----
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


# ---- JSON RESPONSE CLEANING ----
def clean_json_response(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


# ---- RESPONSE VALIDATION ----
def validate_response(data):
    required_keys = ["match_score", "top_strengths", "skill_gaps", "improvements", "recommendation"]
    for key in required_keys:
        if key not in data:
            return False, f"Missing key: {key}"
    if not isinstance(data["match_score"], (int, float)):
        return False, "match_score must be a number"
    if not isinstance(data["top_strengths"], list):
        return False, "top_strengths must be a list"
    if not isinstance(data["skill_gaps"], list):
        return False, "skill_gaps must be a list"
    if not isinstance(data["improvements"], list):
        return False, "improvements must be a list"
    if not isinstance(data["recommendation"], str):
        return False, "recommendation must be a string"
    return True, "Valid"


# ---- AI RESUME ANALYSIS ----
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
Step 5: For each skill gap generate a specific actionable suggestion.
Step 6: Return your analysis as JSON.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY a JSON object in exactly this format:
{{
    "match_score": 75,
    "top_strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "skill_gaps": ["Gap 1", "Gap 2", "Gap 3"],
    "improvements": [
        "Add Docker to your skills section and mention any containerization experience",
        "Include a REST API project in your projects section with technologies used",
        "Add SQL database experience with specific databases like PostgreSQL or MySQL"
    ],
    "recommendation": "One sentence recommendation here."
}}

Rules:
- match_score must be an integer between 0 and 100
- top_strengths must have EXACTLY 3 items
- skill_gaps must have EXACTLY 3 items
- improvements must have EXACTLY 3 items
- each improvement must be one specific actionable sentence
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


# ---- FULL PIPELINE ----
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


# ---- PARSE ANALYSIS ----
def parse_analysis(result):
    score = result.get("match_score", 0)
    strengths = result.get("top_strengths", [])
    gaps = result.get("skill_gaps", [])
    improvements = result.get("improvements", [])
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
        "improvements": improvements,
        "recommendation": recommendation,
        "is_recommended": score >= MIN_RECOMMENDED_SCORE
    }