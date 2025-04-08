package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

func main() {
	processingTime := getEnvInt("PROCESSING_TIME", 5)
	startHTTPServer(processingTime)
}

func startHTTPServer(processingTime int) {
	http.HandleFunc("/ping", func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		traceID := extractTraceID(r)
		log.Printf("[Request] method=%s path=%s from=%s trace_id=%s",
			r.Method, r.URL.Path, r.RemoteAddr, traceID)

		time.Sleep(time.Duration(processingTime) * time.Second) // Simulate processing

		fmt.Fprintln(w, "pong")

		duration := time.Since(start)
		log.Printf("[Response] path=%s duration=%v trace_id=%s", r.URL.Path, duration, traceID)
	})

	port := ":8080"
	log.Printf("HTTP server started on %s", port)
	log.Fatal(http.ListenAndServe(port, nil))
}

// Try to extract the trace ID from the W3C traceparent header
func extractTraceID(r *http.Request) string {
	traceparent := r.Header.Get("traceparent")
	if traceparent == "" {
		return "-"
	}
	// traceparent format: "00-<trace-id>-<span-id>-<flags>"
	parts := strings.Split(traceparent, "-")
	if len(parts) >= 2 {
		return parts[1]
	}
	return "-"
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
