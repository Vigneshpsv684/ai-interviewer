
from google import genai
from dotenv import load_dotenv
import os
import json


# ==============================
# GEMINI SETUP
# ==============================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# ==============================
# GENERATE QUESTION
# ==============================

def generate_question(role, experience, difficulty, previous_questions):

    prompt = f"""
You are an AI technical interviewer.

Generate ONE technical interview question.

Candidate Role:
{role}

Experience Level:
{experience}

Difficulty:
{difficulty}

Previous Questions:
{previous_questions}

Rules:
- Ask only ONE question.
- Do not provide the answer.
- Do not provide hints.
- The question must be relevant to the candidate's role.
- Do not repeat any previous question.
- Ask a different technical concept from previous questions.
- Keep the question clear and suitable for an interview.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


# ==============================
# EVALUATE ANSWER
# ==============================

def evaluate_answer(question, answer):

    prompt = f"""
You are an AI technical interviewer.

Evaluate the candidate's answer.

Question:
{question}

Candidate Answer:
{answer}

Evaluate based on:

1. Correctness
2. Technical understanding
3. Completeness
4. Clarity

Return ONLY valid JSON in exactly this format:

{{
    "score": 7,
    "feedback": "Short explanation of the answer.",
    "strengths": "What the candidate did well.",
    "improvements": "What the candidate should improve."
}}

Rules:
- Score must be an integer from 0 to 10.
- Do not include markdown.
- Do not include ```json.
- Return only JSON.
"""

    # Send evaluation request to Gemini
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    print("\nGemini Evaluation Response:")
    print(response.text)

    try:

        result = json.loads(response.text)

        return result

    except json.JSONDecodeError:

        print("\nCould not parse Gemini response.")

        return {
            "score": 0,
            "feedback": response.text,
            "strengths": "Unable to parse evaluation.",
            "improvements": "Try again."
        }


# ==============================
# GENERATE FINAL REPORT
# ==============================

def generate_final_report(results, role, experience):

    prompt = f"""
You are an AI technical interviewer.

Generate a final interview report for the candidate.

Candidate Role:
{role}

Experience Level:
{experience}

Interview Results:
{results}

Analyze the candidate based on all answers.

Return ONLY valid JSON in exactly this format:

{{
    "overall_summary": "Short overall assessment of the candidate.",
    "strengths": [
        "Strength 1",
        "Strength 2"
    ],
    "weaknesses": [
        "Weakness 1",
        "Weakness 2"
    ],
    "technical_skills": [
        "Skill 1",
        "Skill 2"
    ],
    "improvements": [
        "Improvement 1",
        "Improvement 2"
    ],
    "final_assessment": "Final assessment of the candidate."
}}

Rules:
- Return only JSON.
- Do not use markdown.
- Do not include ```json.
- Base the report only on the interview results.
- Be concise and professional.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    try:

        result = json.loads(response.text)

        return result

    except json.JSONDecodeError:

        print("\nCould not parse final report.")

        return {
            "overall_summary": response.text,
            "strengths": [],
            "weaknesses": [],
            "technical_skills": [],
            "improvements": [],
            "final_assessment": "Unable to generate structured report."
        }
def generate_resume_question(
    resume_text,
    experience,
    difficulty,
    previous_questions
):

    prompt = f"""
You are an AI technical interviewer.

Generate ONE technical interview question
based specifically on the candidate's resume.

Candidate Experience:
{experience}

Difficulty:
{difficulty}

Resume:
{resume_text}

Previous Questions:
{previous_questions}

Rules:
- Ask exactly ONE question.
- Base the question on skills, projects, technologies,
  education or experience mentioned in the resume.
- Do not repeat previous questions.
- Do not provide the answer.
- Do not provide hints.
- Keep the question suitable for a technical interview.
- Return only the question.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text.strip()