from googleapiclient.discovery import build

from auth import get_google_tasks_credentials

# Get Google Tasks
def get_google_tasks():
    creds = get_google_tasks_credentials()
    service = build("tasks", "v1", credentials=creds)
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get("items", [])
    return items