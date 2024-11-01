# Use a slim Python image as the base (updated to Python 3.10 as per latest standard)
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy necessary files into the container
COPY bot.py /app/bot.py
COPY requirements.txt /app/requirements.txt
COPY .env.example /app/.env  # Rename to .env directly if this is the production environment
COPY todo_list.json /app/todo_list.json  # JSON file for persistent task storage

# Make a directory for logs
RUN mkdir -p /app/logs

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Ensure that .env file is read by python-dotenv and logs are output immediately
ENV PYTHONUNBUFFERED=1

# Set up default environment variables for paths (optional if they're already in .env)
ENV JSON_FILE_PATH=/app/todo_list.json
ENV LOG_DIR=/app/logs

# Run the bot script
CMD ["python", "/app/bot.py"]