# Use a base image for Python (you can choose the version you need)
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app


# Copy the Python application code into the container
COPY . .

RUN tar -xzf beyla-linux-amd64-v2.1.0.tar.gz && \
    mv beyla /usr/local/bin/ && \
    chmod +x /usr/local/bin/beyla && \
    rm beyla-linux-amd64-v2.1.0.tar.gz


# Install the required dependencies for the Python app
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port where the Python app and Beyla metrics will be running
EXPOSE 5000 
EXPOSE 8000

# Set environment variables for Beyla
ENV BEYLA_EXPORTER_ENABLED=true
ENV BEYLA_EXPORTER_PORT=8000
ENV BEYLA_METRICS_PATH=/metrics

#CMD ["python", "app.py"]
CMD ["sh", "-c", "/usr/local/bin/beyla & python app.py"]