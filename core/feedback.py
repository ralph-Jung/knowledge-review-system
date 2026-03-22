"""AI feedback on user answers using Gemini API."""

import json
import os
import re

from google import genai

_SYSTEM_PROMPT = """You are evaluating a student's explanation for spaced repetition review.

Evaluate the student's answer. Consider:
1. Are the key concepts present?
2. Is the causal reasoning correct?
3. Are there any factual errors?
4. Is the explanation clear and complete?

Respond in this exact JSON format (no markdown code blocks):
{
    "quality": "good|partial|incorrect",
    "score": 0-5,
    "feedback": "Detailed feedback explaining what was good and what was missing",
    "missing_concepts": ["concept the student missed"],
    "incorrect_parts": ["any factual errors in the student's answer"]
}

good = captured all key concepts correctly (score 4-5)
partial = some key concepts present but incomplete (score 2-3)
incorrect = major errors or missing most key concepts (score 0-1)

Use the same language as the question."""


def evaluate_answer(question: str, model_answer: str, user_answer: str) -> dict:
    """Evaluate a user's answer against the model answer.

    Returns:
        {
            "quality": "good" | "partial" | "incorrect",
            "score": 0-5,
            "feedback": "detailed feedback...",
            "missing_concepts": ["concept1", ...],
            "incorrect_parts": ["error1", ...],
        }
    """
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={
            "system_instruction": _SYSTEM_PROMPT,
            "max_output_tokens": 1000,
            "response_mime_type": "application/json",
        },
        contents=f"""Question: {question}

Model answer (reference):
{model_answer}

Student's answer:
{user_answer}""",
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)
