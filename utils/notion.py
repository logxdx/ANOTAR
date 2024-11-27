import requests, json, re, os
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


def markdown_to_notion_blocks(content):
    blocks = []
    lines = content.splitlines()

    for line in lines:
        line = line.strip()
        
        # Heading Levels
        if line.startswith("# "):  # H1
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:].strip()}}]
                }
            })
        elif line.startswith("## "):  # H2
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:].strip()}}]
                }
            })
        elif line.startswith("### "):  # H3
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[4:].strip()}}]
                }
            })

        # Bullet Points
        elif line.startswith("- ") or line.startswith("* "):  # Bullet point
            bullet_content = line[2:].strip()
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": parse_rich_text(bullet_content)
                }
            })

        # Equations
        elif re.match(r'^\$\$(.+?)\$\$', line):  # Block LaTeX equation
            equation = re.match(r'^\$\$(.+?)\$\$', line).group(1)
            blocks.append({
                "object": "block",
                "type": "equation",
                "equation": {
                    "expression": equation
                }
            })
        elif re.match(r'\$(.+?)\$', line):  # Inline LaTeX equation
            inline_equation = re.sub(r'\$(.+?)\$', lambda m: m.group(1), line)
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "equation", "equation": {"expression": inline_equation}}]
                }
            })
        
        # Paragraph and Rich Text Formatting
        else:
            rich_text = parse_rich_text(line)  # Convert markdown line to rich text
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": rich_text
                }
            })
    return blocks


def parse_rich_text(line):
    """Converts markdown-styled line into Notion rich text objects with annotations."""
    rich_text_objects = []
    patterns = [
        (r'\*\*\*(.+?)\*\*\*', {"bold": True, "italic": True}),         # Bold + Italic
        (r'\*\*(.+?)\*\*', {"bold": True}),                             # Bold
        (r'\*(.+?)\*', {"italic": True}),                               # Italic
        (r'_(.+?)_', {"underline": True}),                              # Underline
        (r'~~(.+?)~~', {"strikethrough": True}),                        # Strikethrough
        (r'```(.+?)```', {"code": True}),                                   # Inline code
        (r'\[(.+?)\]\((https?://[^\s]+)\)', None),                      # Links
    ]

    pos = 0  # Track the current position in the text
    while pos < len(line):
        match = None
        for pattern, annotations in patterns:
            match = re.search(pattern, line[pos:])
            if match:
                start, end = match.span()
                
                if start > 0:
                    rich_text_objects.append({
                        "type": "text",
                        "text": {"content": line[pos:pos+start]},
                        "annotations": {
                            "bold": False, "italic": False, "strikethrough": False,
                            "underline": False, "code": False, "color": "default"
                        }
                    })

                matched_text = match.group(1)
                if annotations:
                    rich_text_objects.append({
                        "type": "text",
                        "text": {"content": matched_text},
                        "annotations": {**annotations, "color": "default"}
                    })
                else:  # Link handling
                    href = match.group(2)
                    rich_text_objects.append({
                        "type": "text",
                        "text": {"content": matched_text, "link": {"url": href}},
                        "annotations": {
                            "bold": False, "italic": False, "strikethrough": False,
                            "underline": False, "code": False, "color": "default"
                        }
                    })
                pos += end
                break
        else:
            rich_text_objects.append({
                "type": "text",
                "text": {"content": line[pos:]},
                "annotations": {
                    "bold": False, "italic": False, "strikethrough": False,
                    "underline": False, "code": False, "color": "default"
                }
            })
            break

    return rich_text_objects


def create_notion_page(title, content, token=NOTION_API_KEY, database_id=NOTION_DATABASE_ID):

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    blocks = markdown_to_notion_blocks(content)

    data = {
        "parent": { "database_id": database_id },
        "properties": {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        },
        "children": blocks
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("Page created successfully!")
    else:
        print(f"Failed to create page: {response.status_code} - {response.text}")

