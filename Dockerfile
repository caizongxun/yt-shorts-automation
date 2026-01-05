FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p output/videos output/audio output/content logs configs assets/gameplay assets/music

# Set permissions
RUN chmod +x scripts/daily_pipeline.py

# Default command: run the daily pipeline
CMD ["python", "scripts/daily_pipeline.py", "--count", "3"]
