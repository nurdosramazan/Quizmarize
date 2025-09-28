# official Python base image
FROM python:3.11-slim

# working directory inside the container
WORKDIR /app

# environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# system dependencies if needed (e.g., for libraries that need C extensions)
# RUN apt-get update && apt-get install -y

# python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app /app