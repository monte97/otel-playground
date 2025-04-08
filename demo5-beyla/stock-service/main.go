package main

import (
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"strings"
	"time"
)

var logger *slog.Logger

func main() {
	logger = setupLogger()

	processingTime := getEnvInt("PROCESSING_TIME", 5)
	startHTTPServer(processingTime)
}

func setupLogger() *slog.Logger {
	levelStr := getEnv("LOG_LEVEL", "INFO")
	var level slog.Level

	switch strings.ToLower(levelStr) {
	case "debug":
		level = slog.LevelDebug
	case "info":
		level = slog.LevelInfo
	case "warn", "warning":
		level = slog.LevelWarn
	case "error":
		level = slog.LevelError
	default:
		level = slog.LevelInfo
	}

	handler := slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: level,
	})
	return slog.New(handler)
}

func startHTTPServer(processingTime int) {
	http.HandleFunc("/ping", func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		traceID := extractTraceID(r)

		logger.InfoContext(r.Context(), "Received request",
			slog.String("method", r.Method),
			slog.String("path", r.URL.Path),
			slog.String("from", r.RemoteAddr),
			slog.String("trace_id", traceID),
		)

		time.Sleep(time.Duration(processingTime) * time.Second)

		fmt.Fprintln(w, "pong")

		duration := time.Since(start)

		logger.InfoContext(r.Context(), "Response sent",
			slog.String("path", r.URL.Path),
			slog.Duration("duration", duration),
			slog.String("trace_id", traceID),
		)
	})

	port := ":8080"
	logger.Info("HTTP server started", slog.String("port", port))
	if err := http.ListenAndServe(port, nil); err != nil {
		logger.Error("Server error", slog.String("error", err.Error()))
	}
}

func extractTraceID(r *http.Request) string {
	traceparent := r.Header.Get("traceparent")
	if traceparent == "" {
		return "-"
	}
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
		if _, err := fmt.Sscanf(value, "%d", &intValue); err == nil {
			return intValue
		}
	}
	return fallback
}
