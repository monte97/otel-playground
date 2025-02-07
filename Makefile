SHELL := /bin/bash

# API Configuration
API_URL=http://localhost:8090/users
CONTENT_TYPE=Content-Type:application/json

# User Data (Modify as needed)
RAND=$(shell tr -dc A-Za-z0-9 </dev/urandom | head -c 8)
USERNAME=User_$(RAND)
EMAIL=$(RAND)@example.com
PASSWORD=SecurePass123

.PHONY: help start create-user get-users get-user update-user delete-user

start:
	docker-compose down
	export $(echo $(cat .env | sed 's/#.*//g' | sed 's/\r//g' | xargs) | envsubst)
	./configs/setup.sh
	docker-compose up --build -d

stop:
	docker-compose down

help:
	@echo "Available commands:"
	@echo "  make start		       - Bootsup the system"
	@echo "  make create-user      - Create a new user"
	@echo "  make get-users        - Retrieve all users"
	@echo "  make get-user ID=<id> - Retrieve a single user"
	@echo "  make update-user ID=<id> USERNAME=new EMAIL=new - Update user details"
	@echo "  make delete-user ID=<id> - Delete a user"

# Create a User
create-user:
	@curl -X POST "$(API_URL)" -H "$(CONTENT_TYPE)" -d '{"username": "$(USERNAME)", "email": "$(EMAIL)", "password": "$(PASSWORD)"}'

# Retrieve All Users
get-users:
	@curl -X GET "$(API_URL)" -H "$(CONTENT_TYPE)" | jq

# Retrieve a Single User
get-user:
	@if [ -z "$(ID)" ]; then echo "Usage: make get-user ID=<id>"; exit 1; fi
	@curl -X GET "$(API_URL)/$(ID)" -H "$(CONTENT_TYPE)" | jq

# Update a User
update-user:
	@if [ -z "$(ID)" ] || [ -z "$(USERNAME)" ] || [ -z "$(EMAIL)" ]; then echo "Usage: make update-user ID=<id> USERNAME=new EMAIL=new"; exit 1; fi
	@curl -X PUT "$(API_URL)/$(ID)" -H "$(CONTENT_TYPE)" -d '{"username": "$(USERNAME)", "email": "$(EMAIL)"}'

# Delete a User
delete-user:
	@if [ -z "$(ID)" ]; then echo "Usage: make delete-user ID=<id>"; exit 1; fi
	@curl -X DELETE "$(API_URL)/$(ID)" -H "$(CONTENT_TYPE)"
