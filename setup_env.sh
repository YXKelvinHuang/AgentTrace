#!/bin/bash

echo "================================================"
echo "  A-LOG Environment Setup"
echo "================================================"
echo ""

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo ""
echo "Optional: To view OpenTelemetry traces locally, run:"
echo "  docker run -p 4317:4317 -p 16686:16686 jaegertracing/all-in-one:latest"
echo "Then open http://localhost:16686"

echo "Done."
