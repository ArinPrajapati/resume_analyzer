import os
from google import genai
from dotenv import load_dotenv
import re


load_dotenv()

client = genai.Client()
MODEL = "gemini-2.0-flash-lite-001"


def generate_response(jd: str, resume: str) -> dict:
    prompt = f"""
    You are a resume screening assistant.

Compare the following Job Description (JD) and Resume. Analyze and return a JSON object with the following fields:

    - "match_score": A number from 0 to 100 indicating how well the resume matches the JD.
    - "missing_skills": A list of important skills or requirements mentioned in the JD that are not found in the resume .
    - "strengths": A list of key skills, qualifications, or experiences in the resume that match the JD.
    - "recommendation": One brief and actionable suggestion to improve the resume for this specific JD.
    - "summary": A brief summary of the candidate's qualifications in relation to the JD "

    Only return a valid JSON object. Do not include any additional commentary.

    Job Description:    \"\"\"
    {jd}
    \"\"\"

    Resume:
    \"\"\"
    {resume}
    \"\"\"


    Respond ONLY in JSON format as specified.

    """

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )
        text = response.text.strip()
        cleaned_text = re.sub(r"^```json\n|```$", "", text, flags=re.MULTILINE).strip()

        import json

        return json.loads(cleaned_text)

    except Exception as e:
        return {
            "error": "Gemini failed to parse",
            "detail": str(e),
            "raw_response": response.text if response else "",
        }
