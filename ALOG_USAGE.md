# A-LOG Usage Guide

A-LOG instruments agents at runtime to capture three observability surfaces: operational, cognitive, and contextual, using JSONL and OpenTelemetry.

## Quick Start

```python
from alog.auto import init, instrument_agent

init(output_dir="logs", level="INFO")

agent = instrument_agent(YourAgent(), name="MyAgent")
result = agent.run("Your task here")
```

## Selecting Methods

Wrap all public callables (default) or specify:

```python
agent = instrument_agent(YourAgent(), name="MyAgent", methods=["run", "plan_action"]) 
```

## OpenTelemetry Integration (Optional)

```python
from alog.core import ALogger
logger = ALogger(enable_otel=True, otel_service_name="A-LOG-Agent", otel_endpoint="http://localhost:4317")
```

Operational events emit JSON and spans; cognitive events are JSON-only; contextual events emit spans only.

Run Jaeger locally to view spans:

```bash
docker run -p 4317:4317 -p 16686:16686 jaegertracing/all-in-one:latest
```

## Surfaces and Schemas

- **Operational (JSON + OTel)**: execution state, method, status, duration, result summary
- **Cognitive (JSON only)**: thought, plan, reflection, confidence, goal, model
- **Contextual (OTel only)**: operation, source_type, source_name, query, retrieved_count, cache_hit

## Reasoning Trace Extraction

Include reasoning markers in outputs:

```
===REASONING_TRACE_START===
Agent needs to verify steps before summarization.
===REASONING_TRACE_END===
```

A-LOG extracts the reasoning trace and logs it as a cognitive event while returning only the main output to the agent.

## Files Produced

- `logs/operational.jsonl`
- `logs/cognitive.jsonl`
  (contextual logs are OTel-only)

## Summary

- Observer without modification
- Dual observability (JSON offline + OTel live)
- Consistent schemas and span hierarchy
