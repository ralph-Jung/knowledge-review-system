#!/usr/bin/env python3
"""Register all existing knowledge files in the review system."""

from pathlib import Path
from core.review_state import register_new_item, KNOWLEDGE_DIR

def main():
    """Register all .md files in knowledge/ directory."""
    print("🔍 Finding knowledge files...")

    md_files = list(KNOWLEDGE_DIR.glob("*.md"))
    print(f"📚 Found {len(md_files)} markdown files")

    registered = 0
    for md_file in md_files:
        if md_file.name == ".gitkeep":
            continue

        print(f"📝 Registering: {md_file.name}")
        register_new_item(str(md_file))
        registered += 1

    print(f"✅ Registered {registered} files in review system!")

if __name__ == "__main__":
    main()