#!/bin/bash
# Start Jaeger for A-LOG OpenTelemetry tracing

echo "Starting Jaeger All-in-One for A-LOG..."
echo "========================================"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not running."
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1

# Start Jaeger
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

echo ""
echo "✓ Jaeger started successfully!"
echo ""
echo "Access points:"
echo "  - Jaeger UI:        http://localhost:16686"
echo "  - OTLP gRPC:        http://localhost:4317"
echo "  - OTLP HTTP:        http://localhost:4318"
echo ""
echo "To stop Jaeger, run: ./scripts/stop_jaeger.sh"
echo ""
