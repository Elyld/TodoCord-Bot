# TodoCord_Bot

## Overview

**TodoCord_Bot** is a Discord bot that integrates with Todoist to manage a to-do list for a specified project, as well as maintain a local backup in a JSON file. Users can add tasks, mark them as complete, and view all tasks within the Todoist project directly through Discord commands. This bot is intended for managing tasks within the Unraid project in Todoist, syncing them both to Todoist and to a local JSON file.

## Features

- **Add Tasks**: Adds a new task to the Todoist project and syncs it with the local JSON file.
- **Add Subtasks**: Adds a subtask under an existing task in Todoist.
- **Complete Tasks**: Marks a task as completed in both Todoist and the local JSON file.
- **View Tasks**: Lists all current tasks in the Todoist project, including due dates if available.
- **Local Backup**: Keeps a local JSON backup of all tasks to allow for offline access or external manipulation.

## Prerequisites

- **Python 3.9+**
- **Discord Bot Token**
- **Todoist API Token**
- **Docker** (optional, but recommended for running the bot in a contained environment)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/elyld/TodoCord_Bot.git
cd TodoCord_Bot

2. Set Up Environment Variables

For security, it's best to keep sensitive information such as tokens out of the codebase. You can create an .env file to store these securely. Add the following to your .env file:

DISCORD_TOKEN=your_discord_token
TODOIST_API_TOKEN=your_todoist_api_token
UNRAID_PROJECT_ID=your_unraid_project_id

Alternatively, replace these placeholders in the script directly if you're testing locally.

3. Docker Setup (Recommended)

A Dockerfile is provided for easy setup. To build and run the bot in a Docker container:

1. Build the Docker image:

docker build -t tododisc_bot .


2. Run the Docker container:

docker run -d --name tododisc_bot tododisc_bot



4. Running Locally

If you choose to run the bot locally (without Docker):

1. Install Required Python Libraries

Run the following command to install dependencies:

pip install -r requirements.txt


2. Start the Bot

Run the bot with:

python bot.py



Usage

Commands

/add_task

Adds a new task to the Todoist Unraid project and saves it in the local JSON file.

Usage: /add_task task_description

Example: /add_task "Complete server maintenance"


/add_subtask

Adds a subtask under an existing Todoist task.

Usage: /add_subtask parent_task_id subtask_description

Example: /add_subtask 123456 "Update server firmware"


/complete_task

Marks a specified task as completed in both Todoist and the local JSON file.

Usage: /complete_task task_id

Example: /complete_task 123456


/view_tasks

Displays all current tasks in the Todoist project.

Usage: /view_tasks


Project Structure

TodoDisc_Bot/
├── bot.py                # Main bot script
├── Dockerfile            # Dockerfile for building the container
├── todo_list.json        # Local JSON file for task storage
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation

Configuration

In bot.py, update the following lines with your respective tokens and project IDs if not using environment variables:

TODOIST_API_TOKEN = "YOUR_API_TOKEN"
DISCORD_TOKEN = 'YOUR_DISCORD_TOKEN'
UNRAID_PROJECT_ID = "PROJECT_ID"

Make sure to use the absolute path for todo_list.json in Docker:

JSON_FILE_PATH = "/app/todo_list.json"

Troubleshooting

JSONDecodeError: If you experience errors related to JSON decoding, delete the todo_list.json file and restart the bot to generate a fresh file.

Invalid Command: Ensure you have synced the commands by running /sync in your Discord server if commands aren’t appearing.

Docker File Not Found: If Docker reports that todo_list.json is missing, ensure it's present in the build context or created as part of the container setup.


Future Enhancements

Potential features for future versions:

Adding reminders and due dates.

Adding task priority management.

Advanced error handling and logging for improved debugging.


License

This project is licensed under the MIT License.


---

Enjoy using TodoCord_Bot for seamless task management on Discord and Todoist!