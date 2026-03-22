#!/usr/bin/env python3
"""CLI entry point for the Knowledge Review System."""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent / ".env")


def cmd_ingest(args):
    """Ingest knowledge from CLI input or inbox.md."""
    from core.ingest import ingest_from_inbox, ingest_line

    if args.from_inbox:
        print("📥 Processing inbox.md...")
        files = ingest_from_inbox()
        if files:
            print(f"\n✅ Ingested {len(files)} item(s)")
            for f in files:
                print(f"   → {f}")
        else:
            print("📭 No new items in inbox.md")
    elif args.text:
        text = " ".join(args.text)
        print(f"📥 Ingesting: {text[:60]}...")
        filepath = ingest_line(text)
        if filepath:
            print(f"✅ Created: {filepath}")
        else:
            print("❌ Failed to ingest (empty input?)")
    else:
        print("Usage: python cli.py ingest 'topic: explanation #tags'")
        print("       python cli.py ingest --from-inbox")


def cmd_status(args):
    """Show upcoming reviews and statistics."""
    from core.review_state import load_review_log
    from core.spaced_repetition import get_due_items

    log = load_review_log()
    if not log:
        print("📭 No knowledge items registered yet.")
        print("   Use 'python cli.py ingest' to add knowledge.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    due = get_due_items(log, today)

    print(f"📊 Knowledge Review Status ({today})")
    print(f"   Total items: {len(log)}")
    print(f"   Due today:   {len(due)}")
    print()

    if due:
        print("📋 Due for review:")
        for fp in due:
            state = log[fp]
            quality = state["last_quality"] or "new"
            ef = state["easiness_factor"]
            print(f"   • {fp}  [last: {quality}, EF: {ef}]")
    else:
        print("✅ No items due for review today!")

    # Show upcoming
    upcoming = []
    for fp, state in log.items():
        if fp not in due:
            upcoming.append((state["next_review"], fp))
    upcoming.sort()

    if upcoming:
        print(f"\n📅 Upcoming reviews:")
        for date, fp in upcoming[:5]:
            print(f"   • {date}: {fp}")
        if len(upcoming) > 5:
            print(f"   ... and {len(upcoming) - 5} more")


def cmd_review(args):
    """Record a review result."""
    from core.review_state import load_review_log, save_review_log
    from core.spaced_repetition import update_review

    log = load_review_log()
    filepath = args.filepath
    quality = args.quality

    if filepath not in log:
        # Try with knowledge/ prefix
        alt = f"knowledge/{filepath}"
        if alt in log:
            filepath = alt
        else:
            print(f"❌ Not found in review log: {filepath}")
            print("   Available items:")
            for fp in sorted(log.keys()):
                print(f"   • {fp}")
            return

    today = datetime.now().strftime("%Y-%m-%d")
    log = update_review(log, filepath, quality, today)
    save_review_log(log)

    state = log[filepath]
    print(f"✅ Review recorded: {filepath}")
    print(f"   Quality:  {quality}")
    print(f"   Next review: {state['next_review']} ({state['interval_days']} days)")
    print(f"   EF: {state['easiness_factor']}")


def _load_sent_today(today: str) -> list[str]:
    """Load list of topics already sent today."""
    import json
    sent_file = Path(__file__).resolve().parent / ".sent_today.json"
    if not sent_file.exists():
        return []
    with open(sent_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    if data.get("date") != today:
        return []
    return data.get("sent", [])


def _save_sent_today(today: str, sent: list[str]) -> None:
    """Save list of topics sent today."""
    import json
    sent_file = Path(__file__).resolve().parent / ".sent_today.json"
    with open(sent_file, "w", encoding="utf-8") as f:
        json.dump({"date": today, "sent": sent}, f, ensure_ascii=False)


def cmd_send_review(args):
    """Select ONE random due topic, generate 3 questions, and send review email."""
    import random

    from core.email_sender import send_review_email
    from core.question_generator import generate_questions
    from core.review_state import load_review_log
    from core.spaced_repetition import get_due_items

    log = load_review_log()
    today = datetime.now().strftime("%Y-%m-%d")
    due = get_due_items(log, today)

    if not due:
        print("✅ No items due for review today. No email sent.")
        return

    # Exclude topics already sent today (3 emails/day, each different topic)
    sent_today = _load_sent_today(today)
    remaining = [fp for fp in due if fp not in sent_today]

    if not remaining:
        print("✅ All due topics already sent today. No email sent.")
        return

    # Pick one random topic
    filepath = random.choice(remaining)

    from core.review_state import BASE_DIR

    abs_path = BASE_DIR / filepath
    if not abs_path.exists():
        print(f"⚠️  File not found: {filepath}")
        return

    try:
        import frontmatter

        with open(abs_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
        title = post.metadata.get("title", Path(filepath).stem)

        print(f"📚 Generating 3 questions for: {title}")
        questions = generate_questions(str(abs_path), num_questions=3)

        items = [{
            "title": title,
            "filepath": filepath,
            "questions": questions,
        }]

        print(f"\n✉️  Sending review email...")
        send_review_email(items, today)

        # Track this topic as sent today
        sent_today.append(filepath)
        _save_sent_today(today, sent_today)

        print("✅ Done!")
    except Exception as e:
        print(f"❌ Failed for {filepath}: {e}")


def cmd_feedback(args):
    """Submit your answer for AI evaluation."""
    from core.feedback import evaluate_answer

    question = args.question
    answer = args.answer

    print("🤖 Evaluating your answer...")
    result = evaluate_answer(
        question=question,
        model_answer=args.model_answer if args.model_answer else "",
        user_answer=answer,
    )

    print(f"\n📊 Quality: {result['quality']} (score: {result['score']}/5)")
    print(f"\n💬 Feedback:\n{result['feedback']}")

    if result.get("missing_concepts"):
        print(f"\n⚠️  Missing concepts:")
        for c in result["missing_concepts"]:
            print(f"   • {c}")

    if result.get("incorrect_parts"):
        print(f"\n❌ Incorrect parts:")
        for p in result["incorrect_parts"]:
            print(f"   • {p}")


def main():
    parser = argparse.ArgumentParser(
        description="📚 Knowledge Review System - Spaced repetition with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py ingest "tmux: SSH 세션과 독립적으로 실행 #linux #tmux"
  python cli.py ingest --from-inbox
  python cli.py status
  python cli.py review knowledge/tmux.md good
  python cli.py send-review
  python cli.py feedback -q "Explain tmux" -a "tmux is a terminal multiplexer"
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ingest
    p_ingest = subparsers.add_parser("ingest", help="Ingest knowledge")
    p_ingest.add_argument("text", nargs="*", help="One-liner knowledge (topic: explanation #tags)")
    p_ingest.add_argument("--from-inbox", action="store_true", help="Process inbox.md")
    p_ingest.set_defaults(func=cmd_ingest)

    # status
    p_status = subparsers.add_parser("status", help="Show review status")
    p_status.set_defaults(func=cmd_status)

    # review
    p_review = subparsers.add_parser("review", help="Record review result")
    p_review.add_argument("filepath", help="Knowledge file path")
    p_review.add_argument("quality", choices=["good", "partial", "incorrect"], help="Self-assessment")
    p_review.set_defaults(func=cmd_review)

    # send-review
    p_send = subparsers.add_parser("send-review", help="Generate and send review email")
    p_send.add_argument("--max-items", type=int, default=5, help="Max items to review (default: 5)")
    p_send.set_defaults(func=cmd_send_review)

    # feedback
    p_feedback = subparsers.add_parser("feedback", help="Get AI feedback on your answer")
    p_feedback.add_argument("-q", "--question", required=True, help="The review question")
    p_feedback.add_argument("-a", "--answer", required=True, help="Your answer")
    p_feedback.add_argument("-m", "--model-answer", default="", help="Model answer for comparison")
    p_feedback.set_defaults(func=cmd_feedback)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
