# Project Overview

This Python script is used to create or update a database in Notion using the Notion API. It also integrates with Google Tasks API to fetch tasks and task lists, and add them to the Notion database.

## Setup

1. Clone this repository to your local machine.
2. Install the required Python packages by running `pip install -r requirements.txt`.
3. Create a `.env` file in the root directory of the project and add your Notion integration token as `NOTION_TOKEN=<your-token>` and `PARENT_PAGE_ID=<your-page-id>` to specify the parent page for the database in Notion.
4. You need to setup Google Tasks API credentials. Follow the instructions [here](https://developers.google.com/tasks/firstapp) to create a `credentials.json` file. Place this file in the root directory of the project.

## Usage

To run the script, use the command `python main.py`.

## About token.json

The `token.json` file is created by the script to store the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time. 

If you want to setup a new account, delete the `token.json` file. The script will then prompt you to authorize access again.

To use your existing account, just run the script. If the `token.json` file is present and the tokens are valid, the script will use these tokens to authorize requests.

## Note

This script uses the `dotenv` package to load environment variables from the `.env` file. Make sure to not include the `.env` file in your version control system by adding it to `.gitignore`.
