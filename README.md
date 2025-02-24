# 📘 OpenTelemetry PHP User Management API #

This repository is a testing ground for experimenting with OpenTelemetry in a PHP-based User Management API. The project is built using Slim Framework, MySQL, and Docker for containerization.
## 🚀 Features ##

    - 📡 Distributed Tracing with OpenTelemetry
    - 🏗 Containerized Setup using Docker Compose
    - 🔍 User Management API (CRUD operations)
    - 📊 Jaeger Integration for tracing visualization
    - 📡 OTLP Exporter for trace data collection

## 🏗 Setup & Installation ##
1️⃣ Clone the Repository

git clone https://github.com/your-repo/opentelemetry-php-api.git
cd opentelemetry-php-api

2️⃣ Configure the Environment

A `.env` file is included with necessary variables. If needed, adjust values in docker-compose.yml and .env.

3️⃣ Start the Services

```bash
docker-compose up -d
```
This starts:

    php-api: The PHP-based user API
    php-api-db: MySQL database
    otel-collector: OpenTelemetry Collector
    jaeger: UI for viewing traces
    phpmyadmin: Database GUI

4️⃣ Run API Requests

Use the Makefile for easier request execution:

```bash
make create-user
make get-users
make get-user ID=1
make update-user ID=1
make delete-user ID=1
```
Or use cURL:

```bash
curl -X POST http://localhost:8080/users -H "Content-Type: application/json" -d '{"username":"test","email":"test@example.com","password":"secure"}'
```

## 📊 Viewing Traces in Jaeger ##

Once your API is running and handling requests, view traces:

    Open Jaeger UI
    Select user-api as the service
    Click Find Traces to explore collected data

## 🔍 OpenTelemetry Instrumentation ##

Tracing is (manually) added to:

    📌 Database Queries (createUser, getAllUsers, etc.)
    📌 Incoming API Requests (POST /users, GET /users/{id}, etc.)
    📌 Logging Events (e.g., user creation)

🔄 Stopping & Cleaning Up

To stop all containers:

``` bash
docker-compose down
```

🛠 Future Experiments

    📌 Add metrics collection (Prometheus/Grafana)
    📌 Implement log correlation with traces
    📌 Explore different tracing backends (Zipkin)
    📌 Introduce other services built with different languages (Go, Java, C#, python)
    📌 Better documentation for opentelemetry data elaboration pipelines
