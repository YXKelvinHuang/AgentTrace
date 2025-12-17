# Contextual Logs: How They Actually Work

## The Correct Understanding

**Contextual logs are captured AUTOMATICALLY via OpenTelemetry instrumentation.**

They do NOT require manual `record_contextual()` calls. This is the whole point of using OTel!

---

## How It Works

### 1. OpenTelemetry Auto-Instrumentation

When you enable A-LOG with OTel, it automatically instruments common libraries:

```python
from alog.auto import init

init(enable_otel=True, auto_instrument=True)
```

Behind the scenes, this:
- Patches `requests`, `urllib3`, `httpx` to capture HTTP calls
- Patches `redis` to capture cache operations
- Patches `sqlalchemy` to capture database queries
- Patches `pymongo` to capture MongoDB operations

### 2. Automatic Capture

When your agent code does:

```python
import requests

# Your agent makes an HTTP call
response = requests.get("https://api.github.com/users/octocat")
```

**OTel automatically creates a span** with:
- `http.url`: "https://api.github.com/users/octocat"
- `http.method`: "GET"
- `http.status_code`: 200
- `http.response.body.size`: 1234
- `duration_ms`: 145
- And many more attributes!

**You wrote ZERO logging code.** This is automatic.

### 3. These Spans ARE Your Contextual Logs

Those auto-generated spans **ARE** the contextual logs. They show:
- What external systems your agent accessed
- What queries were made
- How long each operation took
- Whether operations succeeded or failed

---

## Architecture

```
Your Agent Code
    ↓
    calls: requests.get("https://api.com")
    ↓
OpenTelemetry Instrumentation (automatic patch)
    ↓
    Creates span with:
      - URL
      - Method
      - Status
      - Duration
      - Headers
      - etc.
    ↓
    Sends to Jaeger/OTel Collector
    ↓
You see it as a "contextual log" in Jaeger UI
```

---

## What Gets Auto-Captured

When you enable auto-instrumentation, these operations are AUTOMATICALLY logged:

### HTTP/API Calls
```python
# Using requests
requests.get("https://api.openai.com/v1/models")
# ↓ Automatically creates span:
#   http.url: https://api.openai.com/v1/models
#   http.method: GET
#   http.status_code: 200
```

### Database Queries
```python
# Using SQLAlchemy
session.execute("SELECT * FROM embeddings WHERE id = 1")
# ↓ Automatically creates span:
#   db.system: postgresql
#   db.statement: SELECT * FROM embeddings WHERE id = 1
#   db.operation: SELECT
```

### Cache Operations
```python
# Using Redis
redis_client.get("user:123")
# ↓ Automatically creates span:
#   db.system: redis
#   db.operation: get
#   db.redis.key: user:123
```

### Vector Store Operations
```python
# Using ChromaDB (if instrumented)
collection.query(query_texts=["AI in healthcare"], n_results=5)
# ↓ Automatically creates span with query details
```

---

## Manual vs Automatic

### ❌ WRONG WAY (Manual Logging):

```python
def search_vector_db(self, query: str):
    results = self.db.search(query)

    # Manual logging - NOT needed!
    _global_logger.record_contextual(
        operation="retrieve",
        source_type="vector_db",
        query=query,
        retrieved_count=len(results)
    )

    return results
```

### ✅ CORRECT WAY (Auto-Instrumentation):

```python
def search_vector_db(self, query: str):
    # Just use the library normally
    results = self.db.search(query)

    # OTel automatically logs:
    # - What database was accessed
    # - What query was made
    # - How long it took
    # - How many results returned

    return results
```

**No logging code needed!**

---

## Why This Is Better

### Automatic Instrumentation:
- ✅ No manual logging code needed
- ✅ Captures ALL operations (even in libraries you don't control)
- ✅ Standard attributes across all HTTP calls, DB queries, etc.
- ✅ Includes details you might forget (headers, connection info, etc.)
- ✅ Works with ANY library that has OTel instrumentation

### Manual Logging:
- ❌ Requires code changes for every operation
- ❌ Easy to forget
- ❌ Inconsistent attribute names
- ❌ Misses details
- ❌ More code to maintain

---

## Setting Up Auto-Instrumentation

### Step 1: Install Instrumentation Libraries

```bash
pip install opentelemetry-instrumentation-requests
pip install opentelemetry-instrumentation-redis
pip install opentelemetry-instrumentation-sqlalchemy
# etc.
```

Or install all at once:
```bash
pip install -r requirements.txt
```

### Step 2: Enable OTel in A-LOG

```python
from alog.auto import init

# Auto-instrumentation enabled by default when OTel is on
init(enable_otel=True)
```

### Step 3: Use Libraries Normally

```python
import requests

class MyAgent:
    def fetch_data(self):
        # Just use requests normally
        response = requests.get("https://api.example.com/data")

        # HTTP call is automatically logged to OTel!
        # No manual logging needed!

        return response.json()
```

### Step 4: View in Jaeger

```bash
# Start Jaeger
./scripts/start_jaeger.sh

# Run your agent
ALOG_ENABLE_OTEL=true python your_agent.py

# View traces
open http://localhost:16686
```

---

## What You See in Jaeger

### Trace Structure:

```
Root Span: MyAgent.run_workflow (operational)
├── Span: MyAgent.fetch_data (operational)
│   └── Span: HTTP GET api.example.com (contextual - AUTO)
├── Span: MyAgent.process_results (operational)
│   └── Span: SELECT * FROM cache (contextual - AUTO)
└── Span: MyAgent.store_results (operational)
    └── Span: Redis SET result:123 (contextual - AUTO)
```

The "contextual" spans are **automatically created** by OTel instrumentation!

---

## When Manual Logging IS Needed

You only need manual `record_contextual()` if:

1. **Using a library without OTel instrumentation**
   ```python
   # Custom vector DB without OTel support
   _global_logger.record_contextual(...)  # OK to use manually
   ```

2. **Adding custom business logic context**
   ```python
   # Adding semantic meaning
   _global_logger.record_contextual(
       operation="retrieve",
       semantic_intent="user_preference_lookup"
   )
   ```

3. **Offline analysis without OTel/Jaeger**
   ```python
   # Want contextual logs in JSONL files
   init(save_contextual_to_file=True)
   _global_logger.record_contextual(...)
   ```

But for standard HTTP, DB, cache operations → **OTel auto-instrumentation is the way**.

---

## Summary

| Aspect | Reality |
|--------|---------|
| **How contextual logs are created** | Automatically by OTel instrumentation |
| **Manual logging needed?** | No (for standard libraries) |
| **What gets captured** | HTTP calls, DB queries, cache ops, etc. |
| **Where to see them** | Jaeger UI |
| **Code changes needed** | None (just enable OTel) |

**Key Point: Contextual logs are automatic when using OTel-instrumented libraries.**

---

## Demo

See the working demo:
```bash
# Start Jaeger
./scripts/start_jaeger.sh

# Run auto-instrumentation demo
ALOG_ENABLE_OTEL=true python src/agents/auto_instrumentation_demo/main.py

# View traces in Jaeger
open http://localhost:16686
```

You'll see HTTP calls to GitHub and JSONPlaceholder APIs automatically logged as contextual spans - with ZERO manual logging code!
