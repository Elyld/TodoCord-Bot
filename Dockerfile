FROM python:3.9-slim

WORKDIR /app

# Copy bot script
COPY bot.py /app/bot.py

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Create the JSON file if it doesn't exist
RUN touch /app/todo_list.json

# Run the bot script
CMD ["python", "/app/bot.py"]