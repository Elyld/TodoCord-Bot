import discord
import json
import os
import requests
from discord.ext import commands
from discord import app_commands
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the absolute path for the JSON file
JSON_FILE_PATH = "/app/todo_list.json"  # Replace this path with the appropriate path in your Docker container

# Load tasks from the JSON file
def load_tasks():
    if not os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'w') as file:
            json.dump({"tasks": [], "last_task_id": 0}, file)  # Create with empty task list and ID counter
        logging.info("Created new todo_list.json file.")

    with open(JSON_FILE_PATH, 'r') as file:
        try:
            data = json.load(file)
            # Ensure last_task_id is treated as an integer
            data["last_task_id"] = int(data.get("last_task_id", 0))
            logging.info(f"Loaded tasks from JSON file: {data}")
            return data
        except json.JSONDecodeError:
            logging.error("Failed to load JSON file due to JSONDecodeError.")
            return {"tasks": [], "last_task_id": 0}

# Save tasks to the JSON file
def save_tasks(data):
    try:
        with open(JSON_FILE_PATH, 'w') as file:
            json.dump(data, file, indent=4)
        logging.info("Tasks successfully saved to todo_list.json.")
    except Exception as e:
        logging.error(f"Failed to save tasks to todo_list.json: {e}")

# Todoist API setup
TODOIST_API_TOKEN = "YOUR_API_TOKEN"
TODOIST_API_URL = "https://api.todoist.com/rest/v2/tasks"
HEADERS = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
UNRAID_PROJECT_ID = "PROJECT ID"  # Replace with the actual project ID for the Unraid project

def create_todoist_task(task_description):
    response = requests.post(
        TODOIST_API_URL,
        headers=HEADERS,
        json={"content": task_description, "project_id": UNRAID_PROJECT_ID}
    )
    if response.ok:
        logging.info(f"Task created in Todoist: {task_description}")
        return response.json().get("id")  # Return Todoist task ID if successful
    logging.error(f"Failed to create Todoist task. Status: {response.status_code}, Response: {response.text}")
    return None

def complete_todoist_task(todoist_task_id):
    response = requests.post(
        f"{TODOIST_API_URL}/{todoist_task_id}/close",
        headers=HEADERS
    )
    if response.ok:
        logging.info(f"Task {todoist_task_id} marked as completed in Todoist.")
    else:
        logging.error(f"Failed to mark Todoist task as completed. Status: {response.status_code}")
    return response.ok  # True if request was successful

# Fetch tasks from Todoist and sync to JSON
def fetch_and_sync_tasks():
    response = requests.get(f"{TODOIST_API_URL}?project_id={UNRAID_PROJECT_ID}", headers=HEADERS)
    if response.ok:
        tasks = response.json()
        save_tasks({"tasks": tasks, "last_task_id": max(int(task["id"]) for task in tasks) if tasks else 0})  # Sync to JSON file
        logging.info("Tasks fetched from Todoist and saved to JSON.")
        return tasks
    logging.error(f"Failed to fetch tasks from Todoist: {response.status_code}")
    return None

# Initialize the bot
DISCORD_TOKEN = 'YOUR_DISCORD_TOKEN'
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
    data["last_task_id"] = task_id  # Increment the last task ID
    todoist_task_id = create_todoist_task(task_description)
    new_task = {
        "id": task_id,
        "task": task_description,
        "completed": False,
        "todoist_id": todoist_task_id  # Store Todoist task ID for future reference
    }
    data["tasks"].append(new_task)
    save_tasks(data)
    
    if todoist_task_id:
        await interaction.response.send_message(f"Task {task_id} added to both Discord and Todoist (Unraid Project): {task_description}")
    else:
        await interaction.response.send_message(f"Task {task_id} added to Discord but failed to sync with Todoist.")

# Slash command to mark a task as completed
@tree.command(name="complete_task", description="Mark a task as completed by ID")
async def complete_task(interaction: discord.Interaction, task_id: int):
    data = load_tasks()
    task = next((task for task in data["tasks"] if task["id"] == task_id), None)

    if task:
        task["completed"] = True
        save_tasks(data)
        
        if task["todoist_id"] and complete_todoist_task(task["todoist_id"]):
            await interaction.response.send_message(f"Task {task_id} marked as completed in both Discord and Todoist.")
        else:
            await interaction.response.send_message(f"Task {task_id} marked as completed in Discord but failed to update in Todoist.")
    else:
        await interaction.response.send_message(f"Task {task_id} not found.")

# Slash command to view all tasks in the project and sync to JSON
@tree.command(name="view_tasks", description="View all tasks in the Todoist project")
async def view_tasks(interaction: discord.Interaction):
    tasks = fetch_and_sync_tasks()
    if not tasks:
        await interaction.response.send_message("No tasks found or failed to retrieve tasks.")
        return

    tasks_message = "**Todoist Project Tasks:**\n"
    for task in tasks:
        task_info = f"- **[{task['id']}]** {task['content']}"
        if 'due' in task and task['due'] is not None:
            task_info += f" (Due: {task['due']['date']})"
        tasks_message += task_info + "\n"

    await interaction.response.send_message(tasks_message)

# Run the bot
client.run(DISCORD_TOKEN)