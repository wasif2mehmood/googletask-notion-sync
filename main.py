import time
from googleapiclient.discovery import build
from config import NOTION_TOKEN
from auth import get_google_tasks_credentials
from notion_utils import manual_inputs, create_or_update_database, add_task_to_database, add_tasklist_to_database
from google_tasks_utils import get_google_tasks

# main
if __name__ == "__main__":
    # Get the Notion credentials
    notion_creds = manual_inputs()
    # Database names
    tasks_db_name = "mytasks"
    tasklist_db_name = "mytasklists"
    # Properties for the databases
    properties = {
        "Name": {"title": {}},
        "ID": {"rich_text": {}},
        "Status": {"rich_text": {}},
        "Due": {"rich_text": {}},
        "Completed": {"rich_text": {}},
        "Notes": {"rich_text": {}},
        "Links": {"rich_text": {}},
        "TaskListID": {"rich_text": {}},
    }
    tasklist_properties = {
        "Name": {"title": {}},
        "ID": {"rich_text": {}},
    }

    tasks_db = create_or_update_database(parent_id=notion_creds, db_name=tasks_db_name, properties=properties)
    tasklist_db = create_or_update_database(parent_id=notion_creds, db_name=tasklist_db_name, properties=tasklist_properties)
    time.sleep(5)
    print(f"\n\nDatabase {tasks_db_name} created or updated at {tasks_db['url']}\n")
    print(f"\n\nDatabase {tasklist_db_name} created or updated at {tasklist_db['url']}\n")

    # Get Google Tasks credentials
    creds = get_google_tasks_credentials()
    service = build("tasks", "v1", credentials=creds)

    # Get all tasks from Google Tasks
    items = get_google_tasks()
    for item in items:
        add_tasklist_to_database(tasklist_db["id"], item)
        tasks = service.tasks().list(tasklist=item["id"], showCompleted=True, showHidden=True).execute().get('items', [])
        for task in tasks:
            add_task_to_database(tasks_db["id"], task)