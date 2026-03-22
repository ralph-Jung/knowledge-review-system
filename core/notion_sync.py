#!/usr/bin/env python3
"""Sync CS knowledge from Notion using direct API calls (without MCP)."""

import json
import os
import re
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import frontmatter
import requests


class NotionSync:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        self.base_url = "https://api.notion.com/v1"

    def search_pages(self, query: str) -> List[Dict]:
        """Search for pages in Notion workspace."""
        url = f"{self.base_url}/search"
        data = {
            "query": query,
            "filter": {"property": "object", "value": "page"},
            "page_size": 100,
        }

        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json().get("results", [])

    def get_page_content(self, page_id: str) -> Dict:
        """Get page metadata and content."""
        # Get page metadata
        page_url = f"{self.base_url}/pages/{page_id}"
        page_response = requests.get(page_url, headers=self.headers)
        page_response.raise_for_status()
        page_data = page_response.json()

        # Get page blocks (content)
        blocks_url = f"{self.base_url}/blocks/{page_id}/children"
        blocks_response = requests.get(blocks_url, headers=self.headers)
        blocks_response.raise_for_status()
        blocks_data = blocks_response.json()

        return {
            "page": page_data,
            "blocks": blocks_data.get("results", []),
        }

    def extract_text_from_rich_text(self, rich_text: List[Dict]) -> str:
        """Extract plain text from Notion rich text objects."""
        return "".join(item.get("plain_text", "") for item in rich_text)

    def block_to_markdown(self, block: Dict) -> str:
        """Convert a Notion block to markdown."""
        block_type = block.get("type", "")

        if block_type == "paragraph":
            text = self.extract_text_from_rich_text(block["paragraph"]["rich_text"])
            return text + "\n\n" if text else ""

        elif block_type == "heading_1":
            text = self.extract_text_from_rich_text(block["heading_1"]["rich_text"])
            return f"# {text}\n\n" if text else ""

        elif block_type == "heading_2":
            text = self.extract_text_from_rich_text(block["heading_2"]["rich_text"])
            return f"## {text}\n\n" if text else ""

        elif block_type == "heading_3":
            text = self.extract_text_from_rich_text(block["heading_3"]["rich_text"])
            return f"### {text}\n\n" if text else ""

        elif block_type == "bulleted_list_item":
            text = self.extract_text_from_rich_text(block["bulleted_list_item"]["rich_text"])
            return f"- {text}\n" if text else ""

        elif block_type == "numbered_list_item":
            text = self.extract_text_from_rich_text(block["numbered_list_item"]["rich_text"])
            return f"1. {text}\n" if text else ""

        elif block_type == "code":
            text = self.extract_text_from_rich_text(block["code"]["rich_text"])
            language = block["code"].get("language", "")
            return f"```{language}\n{text}\n```\n\n" if text else ""

        elif block_type == "child_page":
            title = block["child_page"]["title"]
            return f"[{title}](notion-child-page)\n\n"

        else:
            # Handle other block types as plain text
            if block_type in block and "rich_text" in block[block_type]:
                text = self.extract_text_from_rich_text(block[block_type]["rich_text"])
                return text + "\n\n" if text else ""

        return ""

    def slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        # Remove special characters and convert to lowercase
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        # Replace spaces and multiple hyphens with single hyphen
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

    def build_local_index(self, knowledge_dir: Path) -> Dict[str, Dict]:
        """Build index of existing knowledge files."""
        index = {}

        if not knowledge_dir.exists():
            return index

        for md_file in knowledge_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)

                notion_id = post.metadata.get('notion_id')
                if notion_id:
                    index[notion_id] = {
                        'filepath': str(md_file),
                        'last_edited_time': post.metadata.get('notion_last_edited_time'),
                        'title': post.metadata.get('title', md_file.stem),
                    }
            except Exception as e:
                print(f"⚠️  Error reading {md_file}: {e}")

        return index

    def should_process_page(self, page: Dict, local_index: Dict[str, Dict], target_filename: str) -> bool:
        """Determine if a page should be processed (new or updated based on filename and timestamp)."""
        page_last_edited = page["last_edited_time"]

        # Check if file with same name exists
        target_filepath = f"knowledge/{target_filename}"

        # Find any existing file with the same target filename
        for notion_id, file_info in local_index.items():
            existing_filepath = file_info.get('filepath', '')
            if existing_filepath.endswith(target_filename):
                # File with same name exists, check if newer
                local_last_edited = file_info.get('last_edited_time')
                if not local_last_edited or page_last_edited > local_last_edited:
                    return True  # Page is newer, should update
                return False  # Local file is up to date

        return True  # New file

    def generate_confusion_points(self, title: str, content: str) -> List[str]:
        """Generate confusion points based on topic."""
        # Basic confusion points based on common CS topics
        confusion_map = {
            'smtp': [
                "HTTPS와 SMTP의 역할 구분 (HTTPS는 브라우저-서버 통신, SMTP는 메일서버 간 통신)",
                "MX 레코드와 A 레코드의 차이 (MX는 메일서버 주소, A는 IP 주소)",
                "IMAP과 POP의 차이점을 모르는 경우",
                "DNS 조회 순서를 헷갈리는 경우 (MX 레코드 → A/AAAA 레코드 순)"
            ],
            '운영체제': [
                "멀티프로세서와 멀티코어의 차이를 혼동하는 경우",
                "커널 모드와 사용자 모드의 역할을 헷갈리는 경우",
                "프로세스와 스레드의 차이를 모르는 경우",
                "시스템 콜과 일반 함수 호출의 차이를 이해하지 못하는 경우"
            ],
            '네트워크': [
                "OSI 7계층과 실제 구현의 차이를 모르는 경우",
                "스위치와 라우터의 역할을 혼동하는 경우",
                "TCP와 UDP의 차이점을 정확히 모르는 경우",
                "IP 주소와 MAC 주소의 용도를 헷갈리는 경우"
            ]
        }

        # Find matching confusion points
        title_lower = title.lower()
        for keyword, points in confusion_map.items():
            if keyword in title_lower or keyword in content.lower():
                return points

        # Default confusion points
        return [
            "개념의 정의를 정확히 이해하지 못하는 경우",
            "이론과 실제 적용의 차이를 모르는 경우",
            "관련 개념들 간의 관계를 혼동하는 경우"
        ]

    def save_page_as_markdown(self, page_data: Dict, blocks: List[Dict], knowledge_dir: Path) -> str:
        """Save page content as markdown file with frontmatter."""
        page = page_data["page"]
        title = ""

        # Extract title
        if "properties" in page and "title" in page["properties"]:
            title_prop = page["properties"]["title"]
            if title_prop["type"] == "title" and title_prop["title"]:
                title = self.extract_text_from_rich_text(title_prop["title"])

        if not title:
            title = "Untitled"

        # Convert blocks to markdown
        content = ""
        for block in blocks:
            content += self.block_to_markdown(block)

        # Generate tags based on title and content
        tags = []
        title_lower = title.lower()
        content_lower = content.lower()

        if any(word in title_lower for word in ['운영체제', 'os', 'operating']):
            tags.extend(['operating-system', 'os'])
        if any(word in title_lower for word in ['네트워크', 'network']):
            tags.extend(['network'])
        if any(word in title_lower for word in ['smtp', '메일', 'email']):
            tags.extend(['network', 'smtp', 'email'])
        if any(word in content_lower for word in ['프로세스', 'process']):
            tags.append('process')
        if any(word in content_lower for word in ['스레드', 'thread']):
            tags.append('thread')

        # Remove duplicates
        tags = list(set(tags))
        if not tags:
            tags = ['cs-knowledge']

        # Generate frontmatter
        frontmatter_data = {
            'title': title,
            'tags': tags,
            'created': datetime.now().strftime('%Y-%m-%d'),
            'updated': datetime.now().strftime('%Y-%m-%d'),
            'source': 'notion_cs',
            'notion_id': page["id"],
            'notion_last_edited_time': page["last_edited_time"],
            'difficulty': 'intermediate',
            'confusion_points': self.generate_confusion_points(title, content)
        }

        # Create markdown file
        filename = self.slugify(title) + '.md'
        filepath = knowledge_dir / filename

        # Create full content
        post = frontmatter.Post(content, **frontmatter_data)

        # Ensure directory exists
        knowledge_dir.mkdir(exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))

        return str(filepath)


def main():
    """Main sync function."""
    token = os.environ.get('NOTION_TOKEN')
    if not token:
        print("❌ NOTION_TOKEN environment variable not set")
        return

    # Setup paths
    base_dir = Path(__file__).resolve().parent.parent
    knowledge_dir = base_dir / "knowledge"

    print("🔄 Starting Notion CS knowledge sync...")

    # Initialize sync client
    sync = NotionSync(token)

    # Build local index
    print("📚 Building local knowledge index...")
    local_index = sync.build_local_index(knowledge_dir)
    print(f"   Found {len(local_index)} existing files")

    # Find CS 지식 page first
    print("🔍 Finding CS 지식 main page...")
    cs_pages = sync.search_pages("CS 지식")
    cs_main_page = None

    for page in cs_pages:
        title_prop = page.get("properties", {}).get("title", {})
        if title_prop.get("title"):
            title = title_prop["title"][0]["plain_text"]
            if title == "CS 지식":
                cs_main_page = page
                break

    if not cs_main_page:
        print("❌ CS 지식 page not found!")
        return

    print(f"✅ Found CS 지식 page: {cs_main_page['id']}")

    # Get child pages of CS 지식
    print("📚 Getting CS knowledge child pages...")
    cs_content = sync.get_page_content(cs_main_page["id"])
    all_pages = []

    # Process CS main page child pages
    for block in cs_content["blocks"]:
        if block.get("type") == "child_page":
            child_page_id = block["id"]
            try:
                # Get child page metadata
                child_page_url = f"{sync.base_url}/pages/{child_page_id}"
                child_response = requests.get(child_page_url, headers=sync.headers)
                child_response.raise_for_status()
                child_page = child_response.json()
                all_pages.append(child_page)

                # Get child page's children too (for nested structure)
                child_content = sync.get_page_content(child_page_id)
                for sub_block in child_content["blocks"]:
                    if sub_block.get("type") == "child_page":
                        try:
                            sub_page_id = sub_block["id"]
                            sub_page_url = f"{sync.base_url}/pages/{sub_page_id}"
                            sub_response = requests.get(sub_page_url, headers=sync.headers)
                            sub_response.raise_for_status()
                            sub_page = sub_response.json()
                            all_pages.append(sub_page)
                        except Exception as e:
                            print(f"⚠️  Error getting sub-page {sub_block['id']}: {e}")

            except Exception as e:
                print(f"⚠️  Error getting child page {child_page_id}: {e}")

    print(f"📄 Total unique pages: {len(all_pages)}")

    # Process pages that need updating
    processed = 0
    for page in all_pages:
        # Extract title to generate target filename
        title = ""
        if "properties" in page and "title" in page["properties"]:
            title_prop = page["properties"]["title"]
            if title_prop.get("title"):
                title = sync.extract_text_from_rich_text(title_prop["title"])

        if not title:
            title = "Untitled"

        target_filename = sync.slugify(title) + '.md'

        if sync.should_process_page(page, local_index, target_filename):
            try:
                print(f"⚙️  Processing: {page.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', page['id'])}")

                # Get full page content
                content_data = sync.get_page_content(page["id"])

                # Save as markdown
                filepath = sync.save_page_as_markdown(
                    {"page": page},
                    content_data["blocks"],
                    knowledge_dir
                )

                print(f"✅ Saved: {filepath}")
                processed += 1

            except Exception as e:
                print(f"❌ Error processing page {page['id']}: {e}")

    print(f"\n🎉 Sync complete! Processed {processed} pages")


if __name__ == "__main__":
    main()