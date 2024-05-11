import os
import os.path
from dotenv import load_dotenv
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from notion_client import Client
import notion_client
from notion_client.helpers import get_id

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks.readonly"]

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")

while NOTION_TOKEN == "":
    print("NOTION_TOKEN not found.")
    NOTION_TOKEN = input("Enter your integration token: ").strip()

# Initialize the client
notion = Client(auth=NOTION_TOKEN)


def get_google_tasks_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def manual_inputs(parent_id="") -> str:
    parent_id = os.getenv("PARENT_PAGE_ID", parent_id)
    if parent_id == "":
        is_page_ok = False
        while not is_page_ok:
            input_text = input("\nEnter the parent page ID or URL: ").strip()
            try:
                if input_text[:4] == "http":
                    parent_id = get_id(input_text)
                    print(f"\nThe ID of the target page is: {parent_id}")
                else:
                    parent_id = input_text
                notion.pages.retrieve(parent_id)
                is_page_ok = True
                print("Page found")
            except Exception as e:
                print(e)
                continue

    return parent_id


def create_or_update_database(parent_id: str, db_name: str, properties: dict) -> dict:
    results = notion.search(query=db_name).get("results")
    existing_db = next((result for result in results if result["object"] == "database" and result["title"][0]["plain_text"] == db_name), None)

    title = [{"type": "text", "text": {"content": db_name}}]
    icon = {"type": "emoji", "emoji": "🎉"}

    if existing_db:
        try:
            notion.databases.retrieve(existing_db["id"])  # Check if the database exists
            print(f"\n\nUpdating database '{db_name}'...")
            return notion.databases.update(
                database_id=existing_db["id"],
                title=title,
                icon=icon
            )
        except notion_client.errors.APIResponseError:
            print(f"\n\nDatabase '{db_name}' not found, creating a new one...")
    else:
        print(f"\n\nCreating database '{db_name}'...")
    
    return notion.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=title,
        properties=properties,
        icon=icon
    )


def add_task_to_database(database_id: str, task: dict):
    # Fetch all tasks from the database
    existing_tasks = notion.databases.query(database_id=database_id).get("results")

    # Check if a task with the same ID already exists
    for existing_task in existing_tasks:
        if existing_task["properties"]["ID"]["rich_text"][0]["text"]["content"] == task.get('id', 'N/A'):
            print(f"Task '{task.get('title', 'N/A')}' with ID '{task.get('id', 'N/A')}' already exists. Skipping.")
            return

    properties = {
        "Name": {"title": [{"type": "text", "text": {"content": task.get('title', 'N/A')}}]},
        "ID": {"rich_text": [{"type": "text", "text": {"content": task.get('id', 'N/A')}}]},
        "Status": {"rich_text": [{"type": "text", "text": {"content": task.get('status', 'N/A')}}]},
        "Due": {"rich_text": [{"type": "text", "text": {"content": task.get('due', 'N/A')}}]},
        "Completed": {"rich_text": [{"type": "text", "text": {"content": task.get('completed', 'N/A')}}]},
        "Notes": {"rich_text": [{"type": "text", "text": {"content": task.get('notes', 'N/A')}}]},
        "Links": {"rich_text": [{"type": "text", "text": {"content": task.get('links', 'N/A') if task.get('links') else 'N/A'}}]},
        "TaskListID": {"rich_text": [{"type": "text", "text": {"content": task.get('id', 'N/A')}}]},
    }
    return notion.pages.create(parent={"type": "database_id", "database_id": database_id}, properties=properties)


def add_tasklist_to_database(database_id: str, tasklist: dict):
    # Fetch all task lists from the database
    existing_tasklists = notion.databases.query(database_id=database_id).get("results")

    # Check if a task list with the same ID already exists
    for existing_tasklist in existing_tasklists:
        if existing_tasklist["properties"]["ID"]["rich_text"][0]["text"]["content"] == tasklist.get('id', 'N/A'):
            print(f"Task list '{tasklist.get('name', 'N/A')}' with ID '{tasklist.get('id', 'N/A')}' already exists. Skipping.")
            return

    properties = {
        "Name": {"title": [{"type": "text", "text": {"content": tasklist.get('title', 'N/A')}}]},
        "ID": {"rich_text": [{"type": "text", "text": {"content": tasklist.get('id', 'N/A')}}]},
    }
    return notion.pages.create(parent={"type": "database_id", "database_id": database_id}, properties=properties)

if __name__ == "__main__":
    parent_id = manual_inputs()
    db_name = "mytasks"
    tasklist_db_name = "mytasklists"  # New database for task lists
    properties = {
        "Name": {"title": {}},
        "ID": {"rich_text": {}},
        "Status": {"rich_text": {}},
        "Due": {"rich_text": {}},
        "Completed": {"rich_text": {}},
        "Notes": {"rich_text": {}},
        "Links": {"rich_text": {}},
        "TaskListID": {"rich_text": {}},  # Add this line
    }
    tasklist_properties = {
        "Name": {"title": {}},
        "ID": {"rich_text": {}},
    }  # Properties for task list database
    newdb = create_or_update_database(parent_id=parent_id, db_name=db_name, properties=properties)
    tasklist_db = create_or_update_database(parent_id=parent_id, db_name=tasklist_db_name, properties=tasklist_properties)  # Create task list database
    time.sleep(5)
    print(f"\n\nDatabase {db_name} created or updated at {newdb['url']}\n")
    print(f"\n\nDatabase {tasklist_db_name} created or updated at {tasklist_db['url']}\n")  # Print task list database URL

    creds = get_google_tasks_credentials()
    service = build("tasks", "v1", credentials=creds)
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get("items", [])
    for item in items:
        add_tasklist_to_database(tasklist_db["id"], item)  # Add to task list database
        tasks = service.tasks().list(tasklist=item["id"], showCompleted=True, showHidden=True).execute().get('items', [])
        for task in tasks:
            add_task_to_database(newdb["id"], task)