"""Generate explanation-based review questions using Gemini API."""

import json
import os
import re

from google import genai
import frontmatter

_SYSTEM_PROMPT = """You are generating review questions for spaced repetition learning.

Generate explanation-based questions that:
- Require the learner to EXPLAIN concepts in their own words (not just recall facts)
- Test understanding of WHY and HOW, not just WHAT
- Target the known confusion points when possible
- Vary in difficulty

Respond in this exact JSON format (no markdown code blocks):
[
    {
        "question": "Explain why...",
        "model_answer": "Detailed model answer demonstrating deep understanding...",
        "difficulty": "easy|medium|hard"
    }
]

Use the same language as the knowledge content. If the content is in Korean, generate questions in Korean."""


def generate_questions(knowledge_path: str, num_questions: int = 3) -> list[dict]:
    """Generate explanation-based questions from a knowledge file.

    Returns list of:
        {"question": "...", "model_answer": "...", "difficulty": "..."}
    """
    with open(knowledge_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    title = post.metadata.get("title", "Unknown")
    tags = post.metadata.get("tags", [])
    confusion_points = post.metadata.get("confusion_points", [])
    content = post.content

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    confusion_str = "\n".join(f"- {cp}" for cp in confusion_points) if confusion_points else "None"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={
            "system_instruction": _SYSTEM_PROMPT,
            "max_output_tokens": 4000,
            "response_mime_type": "application/json",
        },
        contents=f"""Topic: {title}
Tags: {', '.join(tags)}
Known confusion points:
{confusion_str}

Knowledge content:
{content}

Generate {num_questions} questions.""",
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)
