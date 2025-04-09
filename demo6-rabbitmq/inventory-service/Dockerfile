# Use the official Python image from the Docker Hub
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies from your requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Install OpenTelemetry distribution and exporters
RUN pip install opentelemetry-distro opentelemetry-exporter-otlp 
RUN opentelemetry-bootstrap -a install


# Copy the rest of the application code into the container
COPY . .

# Expose the FastAPI application on port 8000
EXPOSE 8000

CMD ["sh", "-c", "opentelemetry-instrument \
    --traces_exporter otlp \
    --logs_exporter console,otlp \
    --metrics_exporter console \
    uvicorn app.main:app --host 0.0.0.0 --port 8000"]
