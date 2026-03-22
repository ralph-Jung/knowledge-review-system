"""SM-2 spaced repetition algorithm implementation."""

from datetime import datetime, timedelta


def sm2(quality: int, repetition: int, easiness: float, interval: int) -> tuple[int, float, int]:
    """Apply SM-2 algorithm to calculate next review schedule.

    Args:
        quality: 0-5 rating (0-2: incorrect, 3: partial, 4-5: good)
        repetition: number of consecutive correct reviews
        easiness: easiness factor (minimum 1.3)
        interval: current interval in days

    Returns:
        (new_repetition, new_easiness, new_interval_days)
    """
    quality = max(0, min(5, quality))

    # Update easiness factor
    new_easiness = easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_easiness = max(1.3, new_easiness)

    if quality >= 3:
        if repetition == 0:
            new_interval = 1
        elif repetition == 1:
            new_interval = 6
        else:
            new_interval = round(interval * new_easiness)
        new_repetition = repetition + 1
    else:
        # Failed: reset
        new_repetition = 0
        new_interval = 1

    return new_repetition, new_easiness, new_interval


QUALITY_MAP = {
    "good": 5,
    "partial": 3,
    "incorrect": 1,
}


def get_due_items(review_log: dict, today: str) -> list[str]:
    """Return list of knowledge file paths due for review on or before today."""
    today_date = datetime.strptime(today, "%Y-%m-%d").date()
    due = []
    for filepath, state in review_log.items():
        next_review = datetime.strptime(state["next_review"], "%Y-%m-%d").date()
        if next_review <= today_date:
            due.append(filepath)
    # Sort by priority: lower easiness factor first (harder items first)
    due.sort(key=lambda fp: review_log[fp]["easiness_factor"])
    return due


def update_review(review_log: dict, filepath: str, quality_label: str, today: str) -> dict:
    """Apply SM-2 update to a knowledge item and return updated log."""
    if filepath not in review_log:
        raise KeyError(f"{filepath} not found in review log")

    quality = QUALITY_MAP.get(quality_label)
    if quality is None:
        raise ValueError(f"Invalid quality: {quality_label}. Use: good, partial, incorrect")

    state = review_log[filepath]
    new_rep, new_ef, new_interval = sm2(
        quality=quality,
        repetition=state["repetition_count"],
        easiness=state["easiness_factor"],
        interval=state["interval_days"],
    )

    today_date = datetime.strptime(today, "%Y-%m-%d").date()
    next_review = today_date + timedelta(days=new_interval)

    state["repetition_count"] = new_rep
    state["easiness_factor"] = round(new_ef, 2)
    state["interval_days"] = new_interval
    state["next_review"] = next_review.strftime("%Y-%m-%d")
    state["last_quality"] = quality_label
    state["history"].append({
        "date": today,
        "quality": quality_label,
        "interval": new_interval,
    })

    return review_log
