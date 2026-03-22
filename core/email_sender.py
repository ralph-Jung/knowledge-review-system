"""Send review emails via SMTP."""

from __future__ import annotations

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def render_email(items: list[dict], date: str) -> str:
    """Render the review email HTML from template."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("review_email.html")
    return template.render(items=items, date=date)


def send_review_email(items: list[dict], date: str | None = None) -> None:
    """Send the review email."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    html_content = render_email(items, date)

    # SMTP config from env
    smtp_host = os.environ["SMTP_HOST"]
    smtp_port = int(os.environ["SMTP_PORT"])
    smtp_user = os.environ["SMTP_USER"]
    smtp_password = os.environ["SMTP_PASSWORD"]
    email_to = os.environ["EMAIL_TO"]

    # Build email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📚 Daily Knowledge Review - {date}"
    msg["From"] = smtp_user
    msg["To"] = email_to

    # Plain text fallback
    plain_parts = [f"Daily Knowledge Review - {date}\n"]
    for item in items:
        plain_parts.append(f"\n{'='*40}\n{item['title']}\n{'='*40}")
        for i, q in enumerate(item["questions"], 1):
            plain_parts.append(f"\nQ{i}. {q['question']}")
            plain_parts.append(f"\n[Answer] {q['model_answer']}\n")

    msg.attach(MIMEText("\n".join(plain_parts), "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    # Send
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, email_to, msg.as_string())

    print(f"✉️  Review email sent to {email_to}")
