"""Manage review_log.json and knowledge file registration."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
REVIEW_LOG_PATH = BASE_DIR / "review_log.json"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"


def load_review_log() -> dict:
    """Load review log from JSON file."""
    if not REVIEW_LOG_PATH.exists():
        return {}
    with open(REVIEW_LOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_review_log(data: dict) -> None:
    """Save review log to JSON file."""
    with open(REVIEW_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def register_new_item(filepath: str, today: str | None = None) -> dict:
    """Register a new knowledge file in the review log with default SM-2 values."""
    if today is None:
        today = datetime.now().strftime("%Y-%m-%d")

    log = load_review_log()

    # Use relative path from project root
    rel_path = str(Path(filepath).relative_to(BASE_DIR)) if Path(filepath).is_absolute() else filepath

    if rel_path not in log:
        log[rel_path] = {
            "easiness_factor": 2.5,
            "interval_days": 0,
            "repetition_count": 0,
            "next_review": today,
            "last_quality": None,
            "history": [],
        }
        save_review_log(log)

    return log


def sync_with_knowledge_dir() -> dict:
    """Sync review log with knowledge directory.

    - Register new .md files not yet in the log
    - Remove entries for deleted files
    """
    log = load_review_log()
    today = datetime.now().strftime("%Y-%m-%d")

    # Find all .md files in knowledge/
    existing_files = set()
    for md_file in KNOWLEDGE_DIR.glob("*.md"):
        rel_path = str(md_file.relative_to(BASE_DIR))
        existing_files.add(rel_path)
        if rel_path not in log:
            log[rel_path] = {
                "easiness_factor": 2.5,
                "interval_days": 0,
                "repetition_count": 0,
                "next_review": today,
                "last_quality": None,
                "history": [],
            }

    # Remove entries for deleted files
    deleted = [fp for fp in log if fp not in existing_files]
    for fp in deleted:
        del log[fp]

    save_review_log(log)
    return log
