import markdown, os, dotenv, requests, json
from bs4 import BeautifulSoup

dotenv.load_dotenv()

# Set your Notion API key
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_API_KEY = "ntn_M96442919408GaEnd2CvdPv99hjRIB9wOPbU7jB4qYR9Lv"

# Set your Notion database ID
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_DB_ID = '4d794eed58044b169594ab934f34b1de'

def markdown_to_notion_blocks(md_content):
    """Convert Markdown content to Notion blocks."""
    html = markdown.markdown(md_content)
    soup = BeautifulSoup(html, "html.parser")
    notion_blocks = []
    
    for element in soup:
        if element.name == "h1":
            notion_blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"text": {"content": element.text}}]}
            })
        elif element.name == "h2":
            notion_blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": element.text}}]}
            })
        elif element.name == "p":
            notion_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": element.text}}]}
            })
        elif element.name == "ul":
            for li in element.find_all("li"):
                notion_blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"text": {"content": li.text}}]}
                })
    
    return notion_blocks

def create_notion_page(title, content, token=None, database_id=None):

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



markdown_content = """
# Title
This is an example summary.

## Detailed Notes
More content goes here with bullet points:
- Point 1
- Point 2
"""

notion_blocks = markdown_to_notion_blocks(markdown_content)
print(notion_blocks)

response = create_notion_page("Test Page", , token=NOTION_API_KEY, database_id=NOTION_DB_ID)
print(response)
