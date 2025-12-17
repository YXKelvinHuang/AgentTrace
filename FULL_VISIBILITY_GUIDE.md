# A-LOG Full Visibility Guide

## Overview: Getting All Your Logs in One Place

A-LOG provides **three observability surfaces** with different export destinations:

| Surface | What It Tracks | JSONL Files | OpenTelemetry |
|---------|----------------|-------------|---------------|
| **Operational** | Method calls, timing, errors | ✅ `logs/operational.jsonl` | ✅ Spans |
| **Cognitive** | Reasoning traces, thoughts | ✅ `logs/cognitive.jsonl` | ✅ Spans |
| **Contextual** | Data retrieval, memory, APIs | ❌ Not in files | ✅ Spans only |

### The Problem
By default, A-LOG only writes to JSONL files, which means:
- ✅ You get operational and cognitive logs
- ❌ You **don't** get contextual logs (they need OpenTelemetry)
- ❌ You can't see traces in a visual UI

### The Solution
Enable OpenTelemetry to get **full visibility**:
- ✅ All operational logs (files + OTel)
- ✅ All cognitive logs (files + OTel)
- ✅ All contextual logs (OTel only)
- ✅ Visual trace timeline in Jaeger UI
- ✅ Correlation between all surfaces

---

## Quick Setup (3 Steps)

### Step 1: Start Jaeger

```bash
# Make sure Docker Desktop is running, then:
./scripts/start_jaeger.sh

# You should see:
# ✓ Jaeger started successfully!
# Access points:
#   - Jaeger UI:        http://localhost:16686
```

**If you don't have Docker**, see [Alternative: Run Jaeger Directly](#alternative-run-jaeger-directly)

### Step 2: Enable OpenTelemetry

Simply set an environment variable before running your agent:

```bash
export ALOG_ENABLE_OTEL=true
```

Or add it inline:
```bash
ALOG_ENABLE_OTEL=true python your_agent.py
```

### Step 3: Run Agent and View

```bash
# Clean old logs
rm -rf logs

# Run demo with OTel enabled
ALOG_ENABLE_OTEL=true python src/agents/contextual_demo/main.py

# Open Jaeger in browser
open http://localhost:16686
```

In Jaeger UI:
1. Select service: **"A-LOG-Agent"**
2. Click **"Find Traces"**
3. Click on any trace to see the timeline
4. Expand spans to see contextual operations

---

## What Each Component Shows

### 1. JSONL Files (Offline Analysis)

**Location**: `logs/` directory

**Operational Logs** (`logs/operational.jsonl`):
```json
{
  "agent": "ContextualAgent",
  "surface": "operational",
  "event": {
    "method": "search_vector_db",
    "status": "complete",
    "duration_sec": 0.312
  }
}
```

**Cognitive Logs** (`logs/cognitive.jsonl`):
```json
{
  "agent": "ReasoningAgent",
  "surface": "cognitive",
  "event": {
    "thought": "Step 1: Analyzing the problem...",
    "goal": "Execute solve_problem"
  }
}
```

**Best for**:
- Post-hoc analysis
- Batch processing
- Data science workflows
- Long-term storage

### 2. Jaeger UI (Real-time Traces)

**Location**: http://localhost:16686

**Shows all three surfaces**:
- Operational spans (method timing)
- Cognitive spans (reasoning)
- Contextual spans (data operations) ⭐

**Contextual Span Example**:
```
Span: ContextualAgent.contextual
Attributes:
  - operation: retrieve
  - source_type: vector_db
  - source_name: embeddings_store
  - query: "AI in healthcare"
  - retrieved_count: 2
  - cache_hit: false
```

**Best for**:
- Real-time debugging
- Performance analysis
- Understanding data flow
- Distributed tracing

---

## Examples by Use Case

### Use Case 1: Debugging Slow Performance

**Goal**: Find out why your agent is slow

```bash
# Start Jaeger
./scripts/start_jaeger.sh

# Run with OTel
ALOG_ENABLE_OTEL=true python your_slow_agent.py

# In Jaeger:
# 1. Search with: minDuration=1s
# 2. Find the slow trace
# 3. Look for long-running spans
# 4. Check if it's a vector DB query, API call, etc.
```

### Use Case 2: Analyzing Cache Efficiency

**Goal**: See how often cache hits vs misses occur

```bash
# Run contextual demo
ALOG_ENABLE_OTEL=true python src/agents/contextual_demo/main.py

# In Jaeger:
# 1. Search for: cache_hit=true
# 2. Search for: cache_hit=false
# 3. Compare counts
```

### Use Case 3: Understanding Data Flow

**Goal**: See what data sources your agent accesses

```bash
# Run your agent
ALOG_ENABLE_OTEL=true python your_agent.py

# In Jaeger:
# 1. Look at trace timeline
# 2. See all contextual spans
# 3. Check source_type tags (vector_db, api, memory, cache)
# 4. Understand the order of operations
```

### Use Case 4: Offline Log Analysis

**Goal**: Process logs with custom scripts

```bash
# Run without OTel (faster, smaller)
python your_agent.py

# Analyze JSONL files
cat logs/operational.jsonl | jq '.event.duration_sec' | stats
python analyze_cognitive_traces.py logs/cognitive.jsonl
```

---

## Configuration Options

### Environment Variables

```bash
# Enable OpenTelemetry
export ALOG_ENABLE_OTEL=true

# Custom endpoint
export ALOG_OTEL_ENDPOINT=http://my-collector:4317

# Then run normally
python your_agent.py
```

### Programmatic Configuration

```python
from alog.auto import init, instrument_agent

# Enable OTel programmatically
init(
    output_dir="logs",
    level="INFO",
    enable_otel=True,
    otel_endpoint="http://localhost:4317"
)

agent = instrument_agent(your_agent, name="MyAgent")
```

### Disable OTel (Default)

```python
# Just don't set ALOG_ENABLE_OTEL
# Or explicitly disable
init(output_dir="logs", enable_otel=False)
```

**When to disable**:
- Production environments without OTel infrastructure
- When you only need operational + cognitive logs
- Performance-critical scenarios
- Offline/batch processing

---

## Architecture

```
┌─────────────────┐
│   Your Agent    │
└────────┬────────┘
         │ (instrumented)
         ▼
┌─────────────────────────────────────┐
│          A-LOG Core                 │
│                                     │
│  ┌──────────┐  ┌──────────────┐   │
│  │ record() │  │ record_      │   │
│  │          │  │ contextual() │   │
│  └────┬─────┘  └──────┬───────┘   │
└───────┼────────────────┼───────────┘
        │                │
        ├────────────────┴─────────┐
        ▼                          ▼
┌───────────────┐       ┌──────────────────┐
│  JSONL Files  │       │  OpenTelemetry   │
│               │       │   (if enabled)   │
│ operational   │       │                  │
│ cognitive     │       │   All surfaces   │
│               │       │   + contextual   │
└───────────────┘       └────────┬─────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Jaeger UI     │
                        │ localhost:16686 │
                        └─────────────────┘
```

---

## Troubleshooting

### Problem: No contextual logs appearing

**Cause**: OTel not enabled

**Solution**:
```bash
# Check initialization output - should say:
# "OpenTelemetry: enabled → http://localhost:4317"

# If not, enable it:
export ALOG_ENABLE_OTEL=true
python your_agent.py
```

### Problem: Jaeger shows no traces

**Check 1**: Is Jaeger running?
```bash
curl http://localhost:16686
# Should return HTML
```

**Check 2**: Is OTel enabled?
```bash
# Should see in output:
# "OpenTelemetry: enabled → http://localhost:4317"
```

**Check 3**: Are there errors?
```bash
# Look for "[OTEL]" warnings in console output
# Check Jaeger logs:
docker logs alog-jaeger
```

### Problem: Docker not running

**Option 1**: Start Docker Desktop
- macOS: Open Docker Desktop from Applications
- Windows: Open Docker Desktop from Start Menu
- Linux: `sudo systemctl start docker`

**Option 2**: Run Jaeger without Docker
See [Alternative: Run Jaeger Directly](#alternative-run-jaeger-directly)

---

## Alternative: Run Jaeger Directly

If you can't use Docker, download Jaeger binary:

```bash
# Download Jaeger (macOS example)
curl -LO https://github.com/jaegertracing/jaeger/releases/download/v1.52.0/jaeger-1.52.0-darwin-amd64.tar.gz
tar -xzf jaeger-1.52.0-darwin-amd64.tar.gz
cd jaeger-1.52.0-darwin-amd64

# Run all-in-one
./jaeger-all-in-one --collector.otlp.enabled=true

# Should see:
# "Jaeger all-in-one is running on :16686"
```

Then use A-LOG normally:
```bash
ALOG_ENABLE_OTEL=true python your_agent.py
```

---

## Production Considerations

### For Production Use:

1. **Use a proper OTel Collector**
   - Don't send directly to Jaeger
   - Use OpenTelemetry Collector as a gateway
   - Configure batching and sampling

2. **Use a scalable backend**
   - Jaeger with Elasticsearch/Cassandra
   - Tempo with S3/GCS
   - Managed services (Honeycomb, Datadog, etc.)

3. **Configure sampling**
   - Don't trace every single operation
   - Use head-based or tail-based sampling
   - Sample based on error rates

4. **Consider costs**
   - OTel adds latency (small but measurable)
   - Storage costs for traces
   - Network egress costs

### For Development:

- ✅ Use Jaeger All-in-One (provided)
- ✅ Enable OTel for debugging sessions
- ✅ Disable OTel for normal development
- ✅ Use JSONL files for most analysis

---

## Summary

### To Get Full Visibility:

1. **Start Jaeger**: `./scripts/start_jaeger.sh`
2. **Enable OTel**: `export ALOG_ENABLE_OTEL=true`
3. **Run agent**: `python your_agent.py`
4. **View traces**: `open http://localhost:16686`

### What You Get:

- ✅ **JSONL files**: Operational + Cognitive (always)
- ✅ **Jaeger UI**: All surfaces including Contextual (when OTel enabled)
- ✅ **Visual timeline**: See exactly what your agent does
- ✅ **Performance insights**: Find bottlenecks instantly
- ✅ **Data flow visibility**: Understand retrieval patterns

**Full visibility = JSONL + Jaeger** 🎯
