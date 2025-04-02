package main

import (
	"fmt"
	"os"
	"time"

	"github.com/streadway/amqp"
)

func main() {
	rabbitmqURL := getEnv("RABBITMQ_URL", "amqp://localhost:5672")
	rabbitmqExchange := getEnv("RABBITMQ_EXCHANGE", "test_topic")
	rabbitmqQueue := getEnv("RABBITMQ_QUEUE", "test_queue")
	rabbitmqRoutingKey := getEnv("RABBITMQ_ROUTING_KEY", "test.key")
	processingTime := getEnvInt("PROCESSING_TIME", 5)

	conn, err := amqp.Dial(rabbitmqURL)
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		panic(err)
	}
	defer ch.Close()

	// Declare topic exchange
	err = ch.ExchangeDeclare(
		rabbitmqExchange,
		"topic",
		true,  // Durable
		false, // Auto-delete
		false,
		false,
		nil,
	)
	if err != nil {
		panic(err)
	}

	// Declare queue
	q, err := ch.QueueDeclare(
		rabbitmqQueue,
		true,  // Durable
		false, // Auto-delete
		false, // Exclusive
		false,
		nil,
	)
	if err != nil {
		panic(err)
	}

	// Bind queue to exchange with routing key
	err = ch.QueueBind(
		q.Name,
		rabbitmqRoutingKey,
		rabbitmqExchange,
		false,
		nil,
	)
	if err != nil {
		panic(err)
	}

	msgs, err := ch.Consume(
		rabbitmqQueue,
		"",
		false, // Auto-Ack disabled
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		panic(err)
	}

	fmt.Println("[*] Waiting for messages. To exit, press CTRL+C")

	for msg := range msgs {
		fmt.Printf("[x] Received %s\n", msg.Body)
		time.Sleep(time.Duration(processingTime) * time.Second) // Simulate processing
		fmt.Println("[x] Done")
		msg.Ack(false)
	}
}

func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}

func getEnvInt(key string, fallback int) int {
	if value, exists := os.LookupEnv(key); exists {
		var intValue int
		fmt.Sscanf(value, "%d", &intValue)
		return intValue
	}
	return fallback
}
