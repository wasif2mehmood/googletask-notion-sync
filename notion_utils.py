from notion_client import Client
import notion_client
from notion_client.helpers import get_id
import os
from config import NOTION_TOKEN

# Initialize the client
notion = Client(auth=NOTION_TOKEN)

# Function to get the credentials for Google Tasks API
def manual_inputs(parent_id=""):
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


# Function to create or update a database in Notion
def create_or_update_database(parent_id: str, db_name: str, properties: dict):
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

# Function to add a task to a database in Notion
def add_task_to_database(database_id: str, task: dict):
    existing_tasks = notion.databases.query(database_id=database_id).get("results")

    for existing_task in existing_tasks:
        if existing_task["properties"]["ID"]["rich_text"][0]["text"]["content"] == task.get('id', 'N/A'):
            # Update the existing task instead of skipping
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
            return notion.pages.update(page_id=existing_task["id"], properties=properties)

    # If no existing task is found, create a new one
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
# Function to add a task list to a database in Notion
def add_tasklist_to_database(database_id: str, tasklist: dict):
    existing_tasklists = notion.databases.query(database_id=database_id).get("results")

    for existing_tasklist in existing_tasklists:
        if existing_tasklist["properties"]["ID"]["rich_text"][0]["text"]["content"] == tasklist.get('id', 'N/A'):
            # print(f"Task list '{tasklist.get('name', 'N/A')}' with ID '{tasklist.get('id', 'N/A')}' already exists. Skipping.")
            return

    properties = {
        "Name": {"title": [{"type": "text", "text": {"content": tasklist.get('title', 'N/A')}}]},
        "ID": {"rich_text": [{"type": "text", "text": {"content": tasklist.get('id', 'N/A')}}]},
    }
    return notion.pages.create(parent={"type": "database_id", "database_id": database_id}, properties=properties)