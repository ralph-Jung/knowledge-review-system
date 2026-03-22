"""Ingest knowledge from one-liners into structured markdown files."""

from __future__ import annotations

import json
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from google import genai
import frontmatter

from core.review_state import BASE_DIR, KNOWLEDGE_DIR, register_new_item

INBOX_PATH = BASE_DIR / "inbox.md"

_SYSTEM_PROMPT = """You are a knowledge structuring assistant. Expand one-liner knowledge entries into structured JSON.

Respond in this exact JSON format (no markdown code blocks):
{
    "summary": "2-3 paragraph detailed explanation of the concept",
    "key_concepts": ["concept1", "concept2", "concept3"],
    "confusion_points": ["common mistake or misconception 1", "common mistake 2"],
    "related_topics": ["related topic 1", "related topic 2"],
    "difficulty": "beginner|intermediate|advanced",
    "suggested_tags": ["tag1", "tag2"]
}

Use the same language as the topic/explanation for the content. If the input is in Korean, respond in Korean. If in English, respond in English."""


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    # Normalize unicode (NFC preserves Korean characters)
    text = unicodedata.normalize("NFC", text)
    # Keep alphanumeric, spaces, hyphens, and non-ASCII (Korean etc.)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text.strip().lower())
    text = re.sub(r"-+", "-", text)
    return text[:80]


def parse_one_liner(line: str) -> dict:
    """Parse a one-liner into topic, explanation, and tags.

    Format: 'topic: explanation #tag1 #tag2'
    """
    line = line.strip()
    if not line:
        return {}

    # Extract tags
    tags = re.findall(r"#(\w+)", line)
    line_without_tags = re.sub(r"\s*#\w+", "", line).strip()

    # Split topic and explanation
    if ":" in line_without_tags:
        parts = line_without_tags.split(":", 1)
        topic = parts[0].strip()
        explanation = parts[1].strip()
    else:
        topic = line_without_tags
        explanation = ""

    return {"topic": topic, "explanation": explanation, "tags": tags}


def expand_with_ai(topic: str, explanation: str, tags: list[str]) -> dict:
    """Use Gemini API to expand a one-liner into structured knowledge."""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    tag_str = ", ".join(tags) if tags else "none specified"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={
            "system_instruction": _SYSTEM_PROMPT,
            "max_output_tokens": 1500,
            "response_mime_type": "application/json",
        },
        contents=f"Topic: {topic}\nExplanation: {explanation}\nTags: {tag_str}",
    )

    text = response.text.strip()
    # Handle potential markdown code block wrapping
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)


def create_knowledge_file(topic: str, explanation: str, tags: list[str], expanded: dict) -> str:
    """Create a structured markdown file in knowledge/ directory."""
    # Merge tags
    all_tags = list(set(tags + expanded.get("suggested_tags", [])))

    # Create frontmatter
    metadata = {
        "title": topic,
        "tags": all_tags,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "source": "ingest",
        "difficulty": expanded.get("difficulty", "intermediate"),
        "confusion_points": expanded.get("confusion_points", []),
    }

    # Build content
    content_parts = [
        expanded.get("summary", ""),
        "",
        "## Key Concepts",
        "",
    ]
    for concept in expanded.get("key_concepts", []):
        content_parts.append(f"- {concept}")

    content_parts.extend(["", "## Related Topics", ""])
    for topic_name in expanded.get("related_topics", []):
        content_parts.append(f"- {topic_name}")

    body = "\n".join(content_parts)

    # Create post with frontmatter
    post = frontmatter.Post(body, **metadata)

    # Write file
    slug = slugify(topic)
    filepath = KNOWLEDGE_DIR / f"{slug}.md"

    # Avoid overwriting
    counter = 1
    while filepath.exists():
        filepath = KNOWLEDGE_DIR / f"{slug}-{counter}.md"
        counter += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    # Register in review log
    register_new_item(str(filepath))

    return str(filepath)


def ingest_line(line: str) -> str | None:
    """Ingest a single one-liner and return the created file path."""
    parsed = parse_one_liner(line)
    if not parsed:
        return None

    expanded = expand_with_ai(parsed["topic"], parsed["explanation"], parsed["tags"])
    filepath = create_knowledge_file(
        parsed["topic"], parsed["explanation"], parsed["tags"], expanded
    )
    return filepath


def ingest_from_inbox() -> list[str]:
    """Process all lines from inbox.md and return list of created file paths."""
    if not INBOX_PATH.exists():
        return []

    with open(INBOX_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    created_files = []
    remaining_lines = []

    for line in lines:
        stripped = line.strip()
        # Skip comments and empty lines
        if not stripped or stripped.startswith("#") or stripped.startswith("<!--"):
            remaining_lines.append(line)
            continue

        try:
            filepath = ingest_line(stripped)
            if filepath:
                created_files.append(filepath)
                print(f"  ✓ Ingested: {stripped[:50]}... → {filepath}")
            else:
                remaining_lines.append(line)
        except Exception as e:
            print(f"  ✗ Failed to ingest: {stripped[:50]}... ({e})")
            remaining_lines.append(line)

    # Rewrite inbox with only unprocessed lines
    with open(INBOX_PATH, "w", encoding="utf-8") as f:
        f.writelines(remaining_lines)

    return created_files

