- monitoring: LGTM stack
- demo1-php: a simple php API with manual instrumentation
- demo2-python: two interacting api in python with manual instrumentation

# Intro

# Demo 0

Before running any demo, launch the monitoring infrastructure

```bash
cd monitoring-prod
make start
```

# Demo 2

The **Demo 2** consists of two Python services that use manual instrumentation.  
The goal of this demo is to demonstrate how telemetry works when multiple interconnected services are involved.

## Setup

```bash
cd demo2-python
make start
```

## Services Overview

1. **Product Service** (`product`): Manages a product catalog.
2. **Order Service** (`order`): Allows the creation of orders.

When an order is created, the system checks the availability of the specified product.

## Service Endpoints

- The **Order Service** runs on port **8001**.
- The **Product Service** runs on port **8002**.
- Both services provide a Swagger interface at the `/docs` route to test the available APIs.

For a detailed explanation of this demo, refer to **Chapter XYZ**.

# Demo 4 - autoinst

Like `demo2` but wit full autoinstrumentation, no changes on the code