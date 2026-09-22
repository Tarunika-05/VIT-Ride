# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY app.py /app
COPY requirements.txt /app
# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Define environment variable



# Run the application
CMD ["uvicorn","app:app","--reload","--host","0.0.0.0"]