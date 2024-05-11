import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks.readonly"]
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")