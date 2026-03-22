
"""Tests for knowledge ingestion (parsing only, no API calls)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.ingest import parse_one_liner, slugify


def test_parse_one_liner_full():
    """Should parse topic, explanation, and tags."""
    result = parse_one_liner("Python GIL: prevents true multi-threading in CPython #python #concurrency")
    assert result["topic"] == "Python GIL"
    assert result["explanation"] == "prevents true multi-threading in CPython"
    assert set(result["tags"]) == {"python", "concurrency"}


def test_parse_one_liner_no_tags():
    """Should work without tags."""
    result = parse_one_liner("tmux: runs independently from SSH sessions")
    assert result["topic"] == "tmux"
    assert result["explanation"] == "runs independently from SSH sessions"
    assert result["tags"] == []


def test_parse_one_liner_no_colon():
    """Should treat entire line as topic if no colon."""
    result = parse_one_liner("something without explanation #misc")
    assert result["topic"] == "something without explanation"
    assert result["explanation"] == ""
    assert result["tags"] == ["misc"]


def test_parse_one_liner_empty():
    """Should return empty dict for empty input."""
    assert parse_one_liner("") == {}
    assert parse_one_liner("   ") == {}


def test_slugify():
    """Should create URL-friendly slugs."""
    assert slugify("Python GIL") == "python-gil"
    assert slugify("Hello World!") == "hello-world"
    assert slugify("  spaces  everywhere  ") == "spaces-everywhere"


def test_slugify_korean():
    """Should handle Korean characters."""
    slug = slugify("파이썬 GIL")
    assert "파이썬" in slug
    assert "gil" in slug
