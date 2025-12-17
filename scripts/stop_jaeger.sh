#!/bin/bash
# Stop Jaeger for A-LOG OpenTelemetry tracing

echo "Stopping Jaeger..."
echo "=================="
echo ""

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1

# Stop Jaeger
if command -v docker-compose &> /dev/null; then
    docker-compose down
else
    docker compose down
fi

echo ""
echo "✓ Jaeger stopped successfully!"
echo ""
