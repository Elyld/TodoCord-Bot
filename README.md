TodoCord_Bot

Overview

TodoCord_Bot is a Discord bot integrated with Todoist, enabling task management directly from Discord for a specified Todoist project. Designed for easy integration within a Docker environment, it provides seamless task syncing between Todoist and a local JSON backup file.

Features

Add Tasks: Create tasks in both Todoist and the local JSON backup.

Complete Tasks: Mark tasks as completed in both Todoist and locally.

View Tasks: List all tasks in the Todoist project, showing due dates if available.

Local Backup: Maintain a JSON file backup for offline access and data persistence.


Prerequisites

Python 3.9+

Discord Bot Token

Todoist API Token

Docker (recommended for production deployment)


Getting Started

1. Clone the Repository

git clone https://github.com/elyld/TodoCord_Bot.git
cd TodoCord_Bot

2. Set Up Environment Variables

Create an .env file in the project root, filling in the necessary values:

DISCORD_TOKEN=your_discord_token
TODOIST_API_TOKEN=your_todoist_api_token
UNRAID_PROJECT_ID=your_unraid_project_id

3. Docker Setup (Recommended)

This bot is optimized for Docker deployment. Use the following steps to build and run the Docker container.

Build the Docker Image

docker build -t todocord_bot .

Run the Docker Container

docker run -d --name todocord_bot --env-file .env todocord_bot

For persistent task storage, you can mount a volume to save todo_list.json outside the container:

docker run -d --name todocord_bot --env-file .env -v $(pwd)/todo_list.json:/app/todo_list.json todocord_bot

4. Running Locally

To run the bot locally without Docker:

1. Install Dependencies:

pip install -r requirements.txt


2. Start the Bot:

python bot.py



Usage

Commands

/add_task

Adds a new task to the Todoist project and local JSON file.

Usage: /add_task <task_description>

Example: /add_task "Finish the report"

/complete_task

Marks a specified task as completed in both Todoist and the JSON file.

Usage: /complete_task <local_task_id>

Example: /complete_task 1

/view_tasks

Displays all current tasks in the Todoist project.

Usage: /view_tasks

Project Structure

TodoCord_Bot/
├── bot.py               # Main bot script
├── Dockerfile           # Dockerfile for building the container
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore file
├── todo_list.json       # JSON file for task storage
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation

Troubleshooting

JSONDecodeError: If you encounter JSON decoding errors, delete todo_list.json and restart the bot to generate a new file.

Missing Commands: If commands are missing in Discord, ensure the bot has permissions and /sync the commands if necessary.


License

This project is licensed under the MIT License.

