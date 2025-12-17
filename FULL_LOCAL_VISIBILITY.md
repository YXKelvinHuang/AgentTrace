# A-LOG: Full Local Visibility (No Docker Required!)

## TL;DR

**You now have ALL THREE surfaces in local JSONL files!** 🎉

```bash
# Run any agent
python your_agent.py

# View all logs together
python scripts/view_logs.py

# See all three surfaces:
# ✅ logs/operational.jsonl
# ✅ logs/cognitive.jsonl
# ✅ logs/contextual.jsonl  ← NOW INCLUDED!
```

---

## What Changed?

### Before:
- ✅ Operational → JSONL files
- ✅ Cognitive → JSONL files
- ❌ Contextual → OTel/Jaeger only (required Docker)

### After:
- ✅ Operational → JSONL files
- ✅ Cognitive → JSONL files
- ✅ **Contextual → JSONL files + OTel** (works without Docker!)

---

## How It Works

By default, A-LOG now saves **all three surfaces** to local JSONL files:

```python
from alog.auto import init, instrument_agent

# This is the default - all surfaces saved locally
init(output_dir="logs", save_contextual_to_file=True)

agent = instrument_agent(your_agent, name="MyAgent")
agent.run("task")
```

**Files generated:**
```
logs/
├── operational.jsonl    # Method calls, timing, errors
├── cognitive.jsonl      # Reasoning traces, thoughts
└── contextual.jsonl     # Data retrieval, cache, APIs ⭐ NEW!
```

---

## Viewing All Logs Together

### Option 1: Simple CLI Viewer

```bash
# Summary view
python scripts/view_logs.py

# Detailed view
python scripts/view_logs.py --detailed

# Export to single file
python scripts/view_logs.py --export unified.jsonl
```

### Option 2: Python API

```python
from alog.core import ALogger

logger = ALogger("logs")

# Get all logs
operational = logger.get_logs("operational")
cognitive = logger.get_logs("cognitive")
contextual = logger.get_logs("contextual")  # ← Now available!

# Get stats
stats = logger.get_stats()
print(stats)
# {'operational_events': 20, 'cognitive_events': 0, 'contextual_events': 9, 'total_events': 29}
```

### Option 3: Direct File Access

```bash
# View contextual logs
cat logs/contextual.jsonl | jq '.'

# Search for cache hits
cat logs/contextual.jsonl | jq 'select(.event.cache_hit == true)'

# Find vector DB retrievals
cat logs/contextual.jsonl | jq 'select(.event.source_type == "vector_db")'
```

---

## Contextual Log Structure

```json
{
  "id": "04f567ee-dafa-4876-b1ed-4de51169b26b",
  "timestamp": "2025-10-20T10:19:16.866263+00:00",
  "agent": "ContextualAgent",
  "surface": "contextual",
  "level": "INFO",
  "trace_id": "84ee55bb-1b90-4ed8-b25d-3fdd2b1e91cd",
  "span_id": "2686b9bb-5fde-4192-89b1-9e5edc9e0246",
  "event": {
    "operation": "retrieve",           // retrieve, store, update, delete
    "source_type": "vector_db",        // vector_db, cache, memory, api
    "source_name": "embeddings_store", // specific source name
    "query": "AI in healthcare",       // query used
    "retrieved_count": 2,              // number of items retrieved
    "retrieved_items": [...],          // actual items retrieved
    "provenance": ["doc1", "doc2"],    // source document IDs
    "cache_hit": false,                // cache hit/miss
    "write_value": null,               // value being written (if store)
    "memory_state_hash": null,         // memory state hash
    "metadata": {}                     // additional metadata
  }
}
```

---

## Example: Contextual Demo

```bash
# Run the contextual demo
python src/agents/contextual_demo/main.py

# View all logs
python scripts/view_logs.py
```

**Output:**
```
================================================================================
A-LOG Unified View - All Three Surfaces
================================================================================

📊 Log Counts:
  Operational: 20 events
  Cognitive:   0 events
  Contextual:  9 events
  Total:       29 events

🔗 Traces: 1

================================================================================
Trace Summary
================================================================================

📍 Trace #1: 84ee55bb-1b90...
   Events: 20 operational, 0 cognitive, 9 contextual
   • 2025-10-20T10:19:16 [operational ] ContextualAgent.search_vector_db [start]
   • 2025-10-20T10:19:16 [contextual  ] ContextualAgent retrieve from vector_db [cache MISS]
   • 2025-10-20T10:19:16 [operational ] ContextualAgent.search_vector_db [complete] (0.306s)
   • 2025-10-20T10:19:16 [operational ] ContextualAgent.retrieve_from_cache [start]
   • 2025-10-20T10:19:16 [contextual  ] ContextualAgent retrieve from cache [cache MISS]
   ...
```

---

## When to Use What

### Use JSONL Files (Default) When:
- ✅ You want offline analysis
- ✅ You don't have Docker/Jaeger running
- ✅ You need to process logs with custom scripts
- ✅ You want long-term storage
- ✅ You're doing data science workflows

### Use Jaeger/OTel (Optional) When:
- 📊 You want visual trace timelines
- 🔍 You need real-time debugging
- 🌐 You're doing distributed tracing
- 📈 You want performance analytics UI
- 🎯 You're correlating with other services

### Use Both (Recommended) When:
- 💯 You want complete observability
- 🎯 You need offline analysis + real-time debugging
- 📊 You want the best of both worlds

---

## Configuration Options

### Save All to Files (Default)

```python
init(save_contextual_to_file=True)  # Default behavior
```

### OTel Only for Contextual (Original Behavior)

```python
init(save_contextual_to_file=False)  # Contextual only goes to OTel
```

### With OpenTelemetry Enabled

```python
# Files + Jaeger
init(enable_otel=True, save_contextual_to_file=True)
```

Or via environment variable:
```bash
export ALOG_ENABLE_OTEL=true
python your_agent.py
```

---

## Docker Setup (Optional)

If you want to also use Jaeger for visual traces:

### Step 1: Install Docker

```bash
# You need to run this in Terminal (requires sudo password):
brew install --cask docker

# Then open Docker.app from Applications
```

### Step 2: Start Jaeger

```bash
./scripts/start_jaeger.sh
```

### Step 3: Run with OTel

```bash
ALOG_ENABLE_OTEL=true python your_agent.py
```

### Step 4: View in Jaeger UI

```bash
open http://localhost:16686
```

**But remember:** You don't need Docker for full visibility anymore! All logs are in files.

---

## Migration Guide

### Old Code (Contextual OTel-only):
```python
from alog.auto import init

init()  # Contextual logs only go to OTel
# ❌ No contextual.jsonl file created
```

### New Code (Full local visibility):
```python
from alog.auto import init

init()  # Same call, but now contextual.jsonl is created!
# ✅ All three surfaces in files
```

**No code changes needed!** It just works better now.

---

## Summary

| Feature | Status |
|---------|--------|
| **Operational logs** | ✅ JSONL files |
| **Cognitive logs** | ✅ JSONL files |
| **Contextual logs** | ✅ JSONL files (NEW!) |
| **Docker required** | ❌ No (optional) |
| **Full local visibility** | ✅ Yes |
| **Unified viewer** | ✅ `scripts/view_logs.py` |
| **OTel support** | ✅ Optional |
| **Jaeger UI** | ✅ Optional |

**You now have complete observability without any external dependencies!** 🎉

---

## Next Steps

1. ✅ Run your agents - contextual logs are automatically saved
2. ✅ Use `python scripts/view_logs.py` to see all surfaces together
3. ✅ Analyze contextual logs with jq, pandas, or custom scripts
4. 📊 (Optional) Set up Docker + Jaeger for visual traces
5. 🎯 (Optional) Enable OTel for distributed tracing

**Full visibility = All surfaces in JSONL files + Optional Jaeger UI** 🚀
