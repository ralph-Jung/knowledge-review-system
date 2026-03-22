"""Tests for SM-2 spaced repetition algorithm."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.spaced_repetition import get_due_items, sm2, update_review


def test_sm2_perfect_review_grows_interval():
    """Perfect reviews (quality=5) should increase interval exponentially."""
    rep, ef, interval = sm2(quality=5, repetition=0, easiness=2.5, interval=0)
    assert rep == 1
    assert interval == 1

    rep, ef, interval = sm2(quality=5, repetition=1, easiness=ef, interval=interval)
    assert rep == 2
    assert interval == 6

    rep, ef, interval = sm2(quality=5, repetition=2, easiness=ef, interval=interval)
    assert rep == 3
    assert interval > 6


def test_sm2_fail_resets():
    """Failed review (quality=1) should reset repetition and interval."""
    rep, ef, interval = sm2(quality=1, repetition=5, easiness=2.5, interval=30)
    assert rep == 0
    assert interval == 1


def test_sm2_easiness_floor():
    """Easiness factor should never go below 1.3."""
    _, ef, _ = sm2(quality=0, repetition=0, easiness=1.3, interval=1)
    assert ef >= 1.3

    # Multiple failures
    for _ in range(10):
        _, ef, _ = sm2(quality=0, repetition=0, easiness=ef, interval=1)
    assert ef >= 1.3


def test_sm2_partial_review():
    """Partial review (quality=3) should continue but slow growth."""
    rep, ef, interval = sm2(quality=3, repetition=0, easiness=2.5, interval=0)
    assert rep == 1
    assert interval == 1
    # EF should decrease for quality=3
    assert ef < 2.5


def test_get_due_items():
    """Should return items due on or before today."""
    log = {
        "knowledge/a.md": {
            "next_review": "2026-03-20",
            "easiness_factor": 2.5,
        },
        "knowledge/b.md": {
            "next_review": "2026-03-22",
            "easiness_factor": 2.0,
        },
        "knowledge/c.md": {
            "next_review": "2026-03-25",
            "easiness_factor": 2.5,
        },
    }

    due = get_due_items(log, "2026-03-22")
    assert "knowledge/a.md" in due
    assert "knowledge/b.md" in due
    assert "knowledge/c.md" not in due
    # Lower EF should come first (harder items)
    assert due[0] == "knowledge/b.md"


def test_update_review():
    """Should update review state correctly."""
    log = {
        "knowledge/test.md": {
            "easiness_factor": 2.5,
            "interval_days": 0,
            "repetition_count": 0,
            "next_review": "2026-03-22",
            "last_quality": None,
            "history": [],
        }
    }

    log = update_review(log, "knowledge/test.md", "good", "2026-03-22")
    state = log["knowledge/test.md"]
    assert state["last_quality"] == "good"
    assert state["repetition_count"] == 1
    assert state["interval_days"] == 1
    assert state["next_review"] == "2026-03-23"
    assert len(state["history"]) == 1


def test_update_review_invalid_quality():
    """Should raise ValueError for invalid quality."""
    log = {
        "knowledge/test.md": {
            "easiness_factor": 2.5,
            "interval_days": 0,
            "repetition_count": 0,
            "next_review": "2026-03-22",
            "last_quality": None,
            "history": [],
        }
    }

    try:
        update_review(log, "knowledge/test.md", "amazing", "2026-03-22")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
