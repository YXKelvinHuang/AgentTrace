# OpenTelemetry Setup for Full A-LOG Visibility

This guide shows you how to get **full visibility** of all A-LOG surfaces including contextual logs.

## Quick Start (3 Steps)

### 1. Start Jaeger

```bash
./scripts/start_jaeger.sh
```

This starts Jaeger All-in-One with:
- **Jaeger UI**: http://localhost:16686
- **OTLP gRPC**: http://localhost:4317
- **OTLP HTTP**: http://localhost:4318

### 2. Enable OpenTelemetry in A-LOG

**Option A: Environment Variable (Recommended)**
```bash
export ALOG_ENABLE_OTEL=true
python your_agent.py
```

**Option B: Programmatic**
```python
from alog.auto import init, instrument_agent

init(output_dir="logs", level="INFO", enable_otel=True)
agent = instrument_agent(your_agent, name="YourAgent")
```

**Option C: Custom Endpoint**
```bash
export ALOG_ENABLE_OTEL=true
export ALOG_OTEL_ENDPOINT=http://custom-collector:4317
python your_agent.py
```

### 3. Run Your Agent and View Traces

```bash
# Run the contextual demo
ALOG_ENABLE_OTEL=true python src/agents/contextual_demo/main.py

# Open Jaeger UI
open http://localhost:16686
```

## What You'll See in Jaeger

### All Three Surfaces in One Place

1. **Operational Surface** (Also in JSONL)
   - Method calls with timing
   - Start/complete/error status
   - Duration metrics
   - Error traces

2. **Cognitive Surface** (Also in JSONL)
   - Reasoning traces
   - Thought processes
   - Planning steps
   - Confidence scores

3. **Contextual Surface** (OTel Only! ⭐)
   - Vector database retrievals
   - Memory operations
   - API calls
   - Cache hits/misses
   - Data provenance

### Trace Hierarchy

```
Root Span: ContextualAgent.operational (run method)
├── Child Span: ContextualAgent.operational (search_vector_db)
│   └── Child Span: ContextualAgent.contextual (retrieve from vector_db)
├── Child Span: ContextualAgent.operational (retrieve_from_cache)
│   └── Child Span: ContextualAgent.contextual (retrieve from cache)
└── Child Span: ContextualAgent.operational (call_external_api)
    └── Child Span: ContextualAgent.contextual (retrieve from api)
```

## Jaeger UI Features

### 1. Finding Traces

- **Service**: Select "A-LOG-Agent" (or your custom service name)
- **Operation**: Filter by agent name or surface
- **Tags**: Filter by specific attributes

### 2. Trace View

Click on any trace to see:
- **Timeline**: Visual representation of span durations
- **Span Details**: Click spans to see attributes
- **Tags**: All span attributes (cache_hit, source_type, etc.)
- **Logs**: Any logged events within spans

### 3. Useful Searches

Search by tags:
```
# Find all cache hits
cache_hit=true

# Find vector DB retrievals
source_type=vector_db

# Find errors
error=true

# Find slow operations
minDuration=1s
```

## Data Comparison

| Surface | JSONL Files | OpenTelemetry | Best For |
|---------|-------------|---------------|----------|
| **Operational** | ✅ Yes | ✅ Yes | Method timing, errors |
| **Cognitive** | ✅ Yes | ✅ Yes | Reasoning analysis |
| **Contextual** | ❌ No | ✅ Yes | Data flow, retrieval |

**Why contextual is OTel-only:**
- Contextual logs track data flow and external interactions
- These are best visualized as distributed traces
- OTel provides better correlation with external systems
- Reduces log file size

## Advanced Configuration

### Custom Service Name

```python
from alog.core import ALogger

logger = ALogger(
    output_dir="logs",
    enable_otel=True,
    otel_service_name="MyCustomService",
    otel_endpoint="http://localhost:4317"
)
```

### Using with External OTel Collector

If you're running your own OTel collector:

```bash
export ALOG_ENABLE_OTEL=true
export ALOG_OTEL_ENDPOINT=http://my-collector:4317
```

### Docker Compose for Production

The included `docker-compose.yml` is suitable for development. For production:
- Use a persistent backend (Elasticsearch, Cassandra)
- Configure sampling rates
- Set up proper authentication
- Consider using managed services (Honeycomb, Lightstep, Datadog)

## Troubleshooting

### Jaeger Not Starting

```bash
# Check if Docker is running
docker ps

# Check for port conflicts
lsof -i :16686
lsof -i :4317

# Restart Jaeger
./scripts/stop_jaeger.sh
./scripts/start_jaeger.sh
```

### No Traces Appearing

1. **Check OTel is enabled:**
   ```bash
   # Should see "OpenTelemetry: enabled" in output
   ALOG_ENABLE_OTEL=true python your_agent.py
   ```

2. **Verify Jaeger is running:**
   ```bash
   curl http://localhost:16686
   ```

3. **Check for errors:**
   - Look for "[OTEL]" warnings in console output
   - Check Jaeger logs: `docker logs alog-jaeger`

### OpenTelemetry Dependencies Missing

```bash
# Install OpenTelemetry packages
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc

# Or reinstall from requirements
pip install -r requirements.txt
```

## Examples

### Contextual Logging Demo
```bash
./scripts/start_jaeger.sh
ALOG_ENABLE_OTEL=true python src/agents/contextual_demo/main.py
open http://localhost:16686
```

### Reasoning Trace with OTel
```bash
./scripts/start_jaeger.sh
ALOG_ENABLE_OTEL=true python src/agents/reasoning_test_agent/main.py
open http://localhost:16686
```

### Example Agent with Full Tracing
```bash
./scripts/start_jaeger.sh
ALOG_ENABLE_OTEL=true python src/agents/example_agent/main.py
open http://localhost:16686
```

## Stopping Jaeger

```bash
./scripts/stop_jaeger.sh
```

## Integration with Other Tools

### Prometheus Metrics

Jaeger exports Prometheus metrics on port 14269:
```bash
curl http://localhost:14269/metrics
```

### Export to Other Backends

You can configure A-LOG to send to:
- **Honeycomb**: Set endpoint to your Honeycomb OTLP endpoint
- **Datadog**: Use Datadog Agent with OTLP receiver
- **Grafana Tempo**: Point to Tempo's OTLP endpoint
- **AWS X-Ray**: Use AWS OTel Collector
- **Google Cloud Trace**: Use Google Cloud OTel Collector

## Next Steps

1. ✅ Start Jaeger
2. ✅ Run contextual demo with OTel enabled
3. 📊 Explore traces in Jaeger UI
4. 🔍 Search for specific operations
5. 📈 Analyze performance patterns
6. 🎯 Optimize slow operations

---

**Full visibility = JSONL files (operational + cognitive) + Jaeger (all surfaces including contextual)**
