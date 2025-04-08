FROM python:3.10

WORKDIR /app

# Copia e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install OpenTelemetry distribution and exporters
RUN pip install opentelemetry-distro opentelemetry-exporter-otlp 
RUN opentelemetry-bootstrap -a install

# Copia il codice dell'applicazione
COPY . .

EXPOSE 8001

RUN export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
RUN export OTEL_LOG_LEVEL=debug
RUN export OTEL_PYTHON_LOG_LEVEL=debug

CMD ["sh", "-c", "opentelemetry-instrument \
    --traces_exporter console,otlp \
    --logs_exporter console,otlp \
    --metrics_exporter console \
    uvicorn app.main:app --host 0.0.0.0 --port 8001"]
