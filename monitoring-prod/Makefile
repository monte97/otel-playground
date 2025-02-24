.PHONY: start-stop

start:
	docker-compose down
	export $(echo $(cat .env | sed 's/#.*//g' | sed 's/\r//g' | xargs) | envsubst)
	./configs/setup.sh
	docker-compose up --build -d

stop:
	docker-compose down

