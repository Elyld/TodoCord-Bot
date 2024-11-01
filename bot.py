import discord
import json
import os
import requests
from discord.ext import commands
from discord import app_commands
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging with rotation and console output
LOG_DIR = os.getenv("LOG_DIR", "/app/logs")  # Use /app/logs as the default if not set
LOG_FILE = os.path.join(LOG_DIR, "error.log")

# Ensure log directory exists, and log any issues
try:
    os.makedirs(LOG_DIR, exist_ok=True)
    print(f"Log directory created at: {LOG_DIR}")
except Exception as e:
    print(f"Failed to create log directory {LOG_DIR}: {e}")

# Set up logging with both file and console handlers
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=3 * 1024 * 1024, backupCount=3)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])

# Log initialization success
logging.info(f"Logging initialized. Logs are being written to {LOG_FILE}")

# Load variables from environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
UNRAID_PROJECT_ID = os.getenv("UNRAID_PROJECT_ID")
JSON_FILE_PATH = os.getenv("JSON_FILE_PATH", "/app/todo_list.json")

# Headers for Todoist API requests
TODOIST_API_URL = "https://api.todoist.com/rest/v2/tasks"
HEADERS = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}

# Load tasks from the JSON file and assign local_id
def load_tasks():
    if not os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'w') as file:
            json.dump({"tasks": [], "last_task_id": 0}, file)
        logging.info("Created new todo_list.json file.")

    with open(JSON_FILE_PATH, 'r') as file:
        try:
            data = json.load(file)
            for idx, task in enumerate(data["tasks"], start=1):
                if "local_id" not in task:
                    task["local_id"] = idx
            logging.info(f"Loaded tasks with local IDs: {data}")
            return data
        except json.JSONDecodeError:
            logging.error("Failed to load JSON file due to JSONDecodeError.")
            return {"tasks": [], "last_task_id": 0}

# Save tasks to the JSON file, preserving local IDs
def save_tasks(data):
    try:
        with open(JSON_FILE_PATH, 'w') as file:
            json.dump(data, file, indent=4)
        logging.info("Tasks successfully saved to todo_list.json.")
    except Exception as e:
        logging.error(f"Failed to save tasks to todo_list.json: {e}")

# Create a task in Todoist
def create_todoist_task(task_description):
    response = requests.post(
        TODOIST_API_URL,
        headers=HEADERS,
        json={"content": task_description, "project_id": UNRAID_PROJECT_ID}
    )
    if response.ok:
        logging.info(f"Task created in Todoist: {task_description}")
        return response.json().get("id")
    logging.error(f"Failed to create Todoist task. Status: {response.status_code}, Response: {response.text}")
    return None

# Complete a task in Todoist with additional logging
def complete_todoist_task(todoist_task_id):
    try:
        logging.debug(f"Attempting to mark Todoist task {todoist_task_id} as completed.")
        response = requests.post(
            f"{TODOIST_API_URL}/{todoist_task_id}/close",
            headers=HEADERS
        )
        if response.ok:
            logging.info(f"Task {todoist_task_id} marked as completed in Todoist.")
            return True
        else:
            logging.error(f"Failed to mark Todoist task as completed. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        logging.error(f"Exception occurred while marking Todoist task as completed: {e}")
    return False

# Fetch tasks from Todoist and sync to JSON
def fetch_and_sync_tasks():
    response = requests.get(f"{TODOIST_API_URL}?project_id={UNRAID_PROJECT_ID}", headers=HEADERS)
    if response.ok:
        tasks = response.json()
        for idx, task in enumerate(tasks, start=1):
            task["local_id"] = idx
        save_tasks({"tasks": tasks, "last_task_id": max(int(task["id"]) for task in tasks) if tasks else 0})
        logging.info("Tasks fetched from Todoist and saved to JSON.")
        return tasks
    logging.error(f"Failed to fetch tasks from Todoist: {response.status_code}")
    return None

# Initialize the bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Event handler when the bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await tree.sync()

# Slash command to add a new task
@tree.command(name="add_task", description="Add a new task to the Unraid project on Todoist and Discord to-do list")
async def add_task(interaction: discord.Interaction, task_description: str):
    data = load_tasks()
    task_id = data["last_task_id"] + 1
    data["last_task_id"] = task_id
    todoist_task_id = create_todoist_task(task_description)
    new_task = {
        "id": task_id,
        "task": task_description,
        "completed": False,
        "todoist_id": todoist_task_id,
        "local_id": len(data["tasks"]) + 1
    }
    data["tasks"].append(new_task)
    save_tasks(data)
    
    if todoist_task_id:
        await interaction.response.send_message(f"Task {new_task['local_id']} added to both Discord and Todoist (Unraid Project): {task_description}")
    else:
        await interaction.response.send_message(f"Task {new_task['local_id']} added to Discord but failed to sync with Todoist.")

# Slash command to mark a task as completed
@tree.command(name="complete_task", description="Mark a task as completed by Local ID")
async def complete_task(interaction: discord.Interaction, local_id: int):
    data = load_tasks()
    task = next((task for task in data["tasks"] if task["local_id"] == local_id), None)

    if task:
        task["completed"] = True
        save_tasks(data)
        
        if task.get("todoist_id") and complete_todoist_task(task["todoist_id"]):
            await interaction.response.send_message(f"Task {local_id} marked as completed in both Discord and Todoist.")
        else:
            await interaction.response.send_message(f"Task {local_id} marked as completed in Discord but failed to update in Todoist.")
    else:
        await interaction.response.send_message(f"Task {local_id} not found.")

# Slash command to view all tasks in the project and sync to JSON
@tree.command(name="view_tasks", description="View all tasks in the Todoist project")
async def view_tasks(interaction: discord.Interaction):
    tasks = fetch_and_sync_tasks()
    if not tasks:
        await interaction.response.send_message("No tasks found or failed to retrieve tasks.")
        return

    tasks_message = "**Todoist Project Tasks:**\n"
    for task in tasks:
        task_info = f"- **[Local ID: {task['local_id']}]** {task['content']}"
        if 'due' in task and task['due'] is not None:
            task_info += f" (Due: {task['due']['date']})"
        tasks_message += task_info + "\n"

    await interaction.response.send_message(tasks_message)

# Run the bot
client.run(DISCORD_TOKEN)