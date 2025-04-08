start:
	docker-compose up --build

stop:
	docker-compose down

clean:
	docker-compose down --rmi all --volumes


publish:
	docker run --rm --network=host rabbitmq:4-management bash -c \
		"apt update && apt install -y curl && \
		curl -i -u guest:guest -H \"content-type:application/json\" \
		-XPOST -d '{\"properties\":{},\"routing_key\":\"test_queue\",\"payload\":\"Hello, RabbitMQ!\",\"payload_encoding\":\"string\"}' \
		http://localhost:15672/api/exchanges/%2F/amq.default/publish"