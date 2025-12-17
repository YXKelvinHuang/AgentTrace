# Quick Start

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Optional: run Jaeger locally for OpenTelemetry viewing:

```bash
docker run -p 4317:4317 -p 16686:16686 jaegertracing/all-in-one:latest
```

## Instrument Your Agent

```python
from alog.auto import init, instrument_agent

init(output_dir="logs", level="INFO")

class MyAgent:
    def run(self, task: str) -> str:
        return f"Done: {task}"

agent = instrument_agent(MyAgent(), name="MyAgent")
agent.run("Summarize dataset")
```

This writes JSON logs to `logs/operational.jsonl` and `logs/cognitive.jsonl`.

## Select Methods (Optional)

```python
agent = instrument_agent(MyAgent(), name="MyAgent", methods=["run"])  # only wraps `run`
```

## Enable OpenTelemetry (Optional)

```python
from alog.core import ALogger
logger = ALogger(enable_otel=True, otel_service_name="A-LOG-Agent", otel_endpoint="http://localhost:4317")
```

Operational events emit JSON and spans; contextual events emit spans only.

Open `http://localhost:16686` to view traces.
