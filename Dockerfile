# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download YOLOv3 weights (this is a placeholder - in practice, you'd need to download the weights separately)
# ADD yolov3.weights /app/

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]