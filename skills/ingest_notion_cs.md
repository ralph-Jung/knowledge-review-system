# Skill: ingest_notion_cs

## Description

Fetch CS knowledge pages from Notion via the Notion MCP server and save only new or updated pages as structured markdown files in the `knowledge/` directory.

## Instructions

You MUST complete all steps fully.
Do not stop after displaying content.
Do not only summarize in chat.
You MUST create or update local markdown files when needed.

### Step 1: Search for CS pages in Notion

Use the Notion MCP tools to search for CS-related pages.
Search using relevant queries such as:

- "CS"
- "computer science"
- "operating system"
- "network"
- "algorithms"
- "data structures"

Only keep page results, not databases.

### Step 2: Build local index

Read all existing markdown files in the `knowledge/` directory, if it exists.

From each file's frontmatter, collect:

- `notion_id`
- `notion_last_edited_time`
- file path

Use this to determine whether a Notion page is:

1. new
2. updated
3. unchanged

### Step 3: Determine which pages need processing

For each Notion page found:

- retrieve its metadata
- get its Notion page ID
- get its `last_edited_time`

Then compare with local files:

- If no local file has the same `notion_id`, mark it as `new`
- If a local file has the same `notion_id`, but the Notion `last_edited_time` is newer than the local `notion_last_edited_time`, mark it as `updated`
- Otherwise, mark it as `unchanged`

Only process pages marked as `new` or `updated`.

### Step 4: Fetch full content

For each page marked as `new` or `updated`:

1. retrieve page metadata
2. retrieve block children
3. extract the full content

### Step 5: Convert to markdown

Convert the Notion content into clean markdown.

Requirements:

- preserve headings, paragraphs, bullet lists, numbered lists, and code blocks
- use `# <title>` for the document title
- use `##` and lower headings for sections
- keep the markdown readable and structured

### Step 6: Save or update files (MANDATORY)

You MUST save the processed content into the `knowledge/` directory.

File naming:

- slugify the page title
- use lowercase
- replace spaces with hyphens
- remove special characters

Example:

- `knowledge/operating-system.md`
- `knowledge/network-physical-layer.md`

Frontmatter format:

```yaml
---
title: "<page title>"
tags:
  - <relevant CS tags>
created: "<YYYY-MM-DD>"
updated: "<YYYY-MM-DD>"
source: notion_cs
notion_id: "<notion page id>"
notion_last_edited_time: "<ISO timestamp from Notion>"
difficulty: "<beginner|intermediate|advanced>"
confusion_points:
  - "<common misconception 1>"
  - "<common misconception 2>"
---
```
