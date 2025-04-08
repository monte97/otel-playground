package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

func main() {
	processingTime := getEnvInt("PROCESSING_TIME", 5)

	// Start HTTP server with /ping endpoint
	startHTTPServer(processingTime)
}

func startHTTPServer(processingTime int) {
	http.HandleFunc("/ping", func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		log.Printf("[Request] %s %s from %s", r.Method, r.URL.Path, r.RemoteAddr)

		time.Sleep(time.Duration(processingTime) * time.Second) // Simulate processing time
		fmt.Fprintln(w, "pong")

		duration := time.Since(start)
		log.Printf("[Response] %s completed in %v", r.URL.Path, duration)
	})

	port := ":8080"
	log.Printf("HTTP server started on %s", port)
	log.Fatal(http.ListenAndServe(port, nil))
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
