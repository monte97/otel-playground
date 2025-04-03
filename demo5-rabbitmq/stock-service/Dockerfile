FROM golang:latest

WORKDIR /app

# Download and install Beyla binary
RUN wget https://github.com/grafana/beyla/releases/download/v2.1.0/beyla-linux-amd64-v2.1.0.tar.gz && \
    tar -xzf beyla-linux-amd64-v2.1.0.tar.gz && \
    mv beyla /usr/local/bin/ && \
    chmod +x /usr/local/bin/beyla && \
    rm beyla-linux-amd64-v2.1.0.tar.gz

# Copy go.mod and go.sum first for caching
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of your application files
COPY . .

# Build your application
RUN go build -o main .

EXPOSE 8080

# Execute beyla
#RUN /usr/local/bin/beyla

CMD ["sh", "-c", "/usr/local/bin/beyla & ./main"]