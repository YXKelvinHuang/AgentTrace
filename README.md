# AgentTrace

AgentTrace is a runtime instrumentation and observability system for AI agents. It captures structured logs about operational actions, cognitive reasoning, and contextual interactions.

## 📄 Paper

**AgentTrace: Observability and Reasoning Tracing for AI Agents**  
[Download the full paper (PDF)](paper/AgentTrace.pdf)

## Purpose

- Debug and trace agent execution
- Analyze cognitive reasoning
- Measure latency, performance, and reliability
- Visualize distributed traces across components

## Core Design: Observer Without Modification

```python
from alog.auto import init, instrument_agent

init(output_dir="logs", level="INFO")
agent = instrument_agent(my_agent, name="MyAgent")
```

AgentTrace wraps public callable methods to:
- Log start/complete/error with duration
- Capture outputs (summaries)
- Extract reasoning traces between `===REASONING_TRACE_START===` and `===REASONING_TRACE_END===`

Your agent’s logic remains unchanged.

## Data Surfaces

- **Operational**: JSONL + OpenTelemetry (execution state and timing) - Automatic
- **Cognitive**: JSONL + OpenTelemetry (reasoning traces) - Automatic
- **Contextual**: OpenTelemetry (environment interactions) - **Automatic via OTel instrumentation**

Contextual logs are captured AUTOMATICALLY when you use instrumented libraries (requests, redis, sqlalchemy, etc.). No manual logging needed!

## Outputs

- `logs/operational.jsonl`
- `logs/cognitive.jsonl`
- Contextual spans to your OTel collector (Jaeger/Tempo)

## Enable OpenTelemetry (Get Automatic Contextual Logging!)

To see **all three surfaces** including auto-captured contextual logs:

```bash
# 1. Start Jaeger
./scripts/start_jaeger.sh

# 2. Enable OpenTelemetry
export ALOG_ENABLE_OTEL=true

# 3. Run your agent
python your_agent.py

# 4. View in Jaeger UI
open http://localhost:16686
```

**See**: [FULL_VISIBILITY_GUIDE.md](FULL_VISIBILITY_GUIDE.md) for complete setup instructions.

**Quick setup**: [OTEL_SETUP.md](OTEL_SETUP.md)

## Example Workflow

```python
from alog.auto import init, instrument_agent

init(output_dir="logs", level="INFO")
agent = instrument_agent(my_agent, name="ResearchAgent")

agent.run_analysis("AI security landscape")
agent.plan_action("Draft summary report")
```

Inspect `logs/cognitive.jsonl` for reasoning traces and `logs/operational.jsonl` for runtime stats.

## Span Hierarchy

Operational spans are parents; cognitive and contextual spans are children. All share the same trace via OpenTelemetry context propagation.
