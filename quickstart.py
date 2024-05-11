import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks.readonly"]

def main():
  """Shows basic usage of the Tasks API.
  Prints the title and ID of each task list and the tasks within them.
  """
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

  try:
    service = build("tasks", "v1", credentials=creds)

    # Call the Tasks API
    results = service.tasklists().list().execute()
    items = results.get("items", [])

    if not items:
      print("No task lists found.")
      return

    print("Task lists:")
    for item in items:
      print(f"{item['title']} ({item['id']})")
      tasks = service.tasks().list(tasklist=item["id"], showCompleted=True, showHidden=True).execute().get('items', [])
      
      if not tasks:
        print("No tasks found in this task list.")
      else:
        print("Tasks:")
        for task in tasks:
          print(f"Title: {task.get('title', 'N/A')}")
          print(f"ID: {task.get('id', 'N/A')}")
          print(f"Status: {task.get('status', 'N/A')}")
          print(f"Due: {task.get('due', 'N/A')}")
          print(f"Completed: {task.get('completed', 'N/A')}")
          print(f"Notes: {task.get('notes', 'N/A')}")
          print(f"Links: {task.get('links', 'N/A')}")
          print("------")

  except HttpError as err:
    print(err)

if __name__ == "__main__":
  main()