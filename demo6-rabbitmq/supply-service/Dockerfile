FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install OpenTelemetry distribution and exporters
RUN pip install opentelemetry-distro opentelemetry-exporter-otlp 
RUN opentelemetry-bootstrap -a install

COPY app.py .

CMD ["sh", "-c", "opentelemetry-instrument \
    --traces_exporter otlp \
    --logs_exporter console,otlp \
    --metrics_exporter console \
    uvicorn app:app --host 0.0.0.0 --port 8000"]
