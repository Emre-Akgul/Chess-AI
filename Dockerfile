# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Install necessary system libraries
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    openssl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python packages from requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Generate self-signed SSL certificates
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.example.com"

# Copy your application code
COPY ./app .

# Expose the port the app runs on
EXPOSE 8000

# Define environment variable
ENV NAME World

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile=key.pem", "--ssl-certfile=cert.pem"]
