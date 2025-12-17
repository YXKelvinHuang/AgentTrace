# Financial Agent

A comprehensive financial analysis agent integrated with OpenBB Workspace.

## Overview

The Financial Agent combines multiple capabilities from the agents-for-openbb repository into a single, production-ready agent:

- **Widget Integration**: Seamlessly retrieves and processes data from OpenBB widgets
- **Reasoning Steps**: Provides transparent, step-by-step analysis for users
- **Citations**: Attributes data sources for transparency and traceability
- **Visualizations**: Generates charts (line, bar, scatter, pie, donut)
- **Structured Data**: Creates formatted tables for financial metrics

## Features

### Core Capabilities

1. **Financial Data Analysis**
   - Stock price analysis and trends
   - Fundamental metrics evaluation
   - Options data interpretation
   - Market sentiment analysis

2. **Interactive Widget Support**
   - Automatic widget data retrieval
   - Multi-widget aggregation
   - Parameter-aware processing
   - Dashboard integration

3. **Rich Output Formats**
   - Streaming text responses
   - Dynamic chart generation
   - Formatted data tables
   - Source citations with metadata

### Feature Toggles

Users can enable/disable features in OpenBB Workspace:

- **Enable Charts**: Generate visualizations from financial data
- **Enable Tables**: Display structured data tables
- **Enable Citations**: Show data source attributions

## Installation

### Prerequisites

- Python 3.10+
- OpenAI API key
- OpenBB Workspace (for deployment)

### Quick Setup

1. **Navigate to the agent directory**:
   ```bash
   cd src/agents/financial_agent
   ```

2. **Run the setup script**:
   ```bash
   ./setup.sh
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root (`A-LOG/.env`):
   ```bash
   OPENAI_API_KEY=sk-your-api-key-here
   ```

### Manual Installation

If you prefer manual installation:

```bash
cd src/agents/financial_agent
pip install -r requirements.txt
```

## Usage

### Running Locally

Start the agent server:

```bash
cd src/agents/financial_agent
uvicorn main:app --host 0.0.0.0 --port 7777 --reload
```

The agent will be available at:
- **API**: http://localhost:7777
- **Docs**: http://localhost:7777/docs
- **Agent descriptor**: http://localhost:7777/agents.json

### Connecting to OpenBB Workspace

1. Start the agent locally (see above)
2. In OpenBB Workspace, add custom agent:
   - Go to Settings → Agents
   - Add Custom Agent
   - Enter URL: `http://localhost:7777`
3. The agent will register automatically via `/agents.json`

### Testing

Run the test suite:

```bash
cd src/agents/financial_agent
pytest tests/test_agent.py -v
```

### Example Usage with cURL

**Simple query**:
```bash
curl -X POST http://localhost:7777/v1/query \
  -H "Content-Type: application/json" \
  -d @tests/test_payloads/single_message.json
```

**Query with widget**:
```bash
curl -X POST http://localhost:7777/v1/query \
  -H "Content-Type: application/json" \
  -d @tests/test_payloads/message_with_widget.json
```

## Directory Structure

```
financial_agent/
├── main.py                    # FastAPI application with query endpoint
├── __init__.py                # Package initialization
├── requirements.txt           # Python dependencies
├── setup.sh                   # Automated setup script
├── README.md                  # This file
└── tests/
    ├── test_agent.py          # Test suite
    └── test_payloads/         # Sample request payloads
        ├── single_message.json
        ├── message_with_widget.json
        └── conversation_with_context.json
```

## API Endpoints

### GET /

Returns agent information and status.

### GET /agents.json

Agent registration endpoint for OpenBB Workspace. Defines agent capabilities and features.

### POST /v1/query

Main query processing endpoint. Accepts QueryRequest and returns streaming SSE events.

### GET /health

Health check endpoint.

## Example Interactions

**Basic Query**:
```
User: "What are the key financial metrics for Apple stock?"

Agent: [Reasoning] Starting financial analysis...
       [Response] Key metrics for Apple (AAPL) include:
       - Revenue: Growing at 8% YoY
       - Net Income: $25B (Q4 2024)
       - P/E Ratio: 28.5
       [Table] Displays detailed metrics
       [Chart] Shows revenue trend
```

**Widget Integration**:
```
User: "Analyze the stock price data in this widget"

Agent: [Reasoning] Retrieving data from 1 selected widget(s)...
       [Response] Based on the stock price data:
       - Current price: $175.43 (+1.35%)
       - 5-day trend: Upward momentum
       - Volume: Above average
       [Chart] Visualizes price movement
       [Citations] Links to widget data source
```

## Testing

The test suite includes:

1. **Basic Endpoints** (`TestBasicEndpoints`)
   - Root endpoint
   - Health check
   - Agent registration

2. **Query Processing** (`TestQueryProcessing`)
   - Single message queries
   - Widget data retrieval
   - Conversation with context

3. **Features** (`TestFeatures`)
   - Reasoning steps emission
   - Chart generation
   - Table generation
   - Citations generation

4. **Error Handling** (`TestErrorHandling`)
   - Invalid payloads
   - Empty messages

### Test Payloads

Located in `tests/test_payloads/`:

- **single_message.json**: Basic query without widgets
- **message_with_widget.json**: Query with widget selection
- **conversation_with_context.json**: Multi-turn conversation with widget data

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |

### Feature Flags

Defined in the `/agents.json` endpoint:

```python
"features": {
    "streaming": True,                    # SSE streaming (always on)
    "widget-dashboard-select": True,      # Widget selector UI
    "widget-dashboard-search": True,      # Dashboard widget access
    "enable-charts": {
        "label": "Enable Charts",
        "default": True,
        "description": "Generate visualizations"
    },
    "enable-tables": {
        "label": "Enable Tables",
        "default": True,
        "description": "Display data tables"
    },
    "enable-citations": {
        "label": "Enable Citations",
        "default": True,
        "description": "Show source attributions"
    }
}
```

## Development

### Adding New Features

1. **New reasoning step**:
   ```python
   yield reasoning_step(
       event_type="INFO",
       message="Your custom reasoning step...",
       details={"key": "value"}
   ).model_dump()
   ```

2. **New chart type**:
   ```python
   yield chart(
       type="bar",  # or "scatter", "pie", "donut"
       data=[{"x": 1, "y": 2}, ...],
       x_key="x",
       y_keys=["y"],
       name="Chart Name",
       description="Chart description"
   ).model_dump()
   ```

3. **New table**:
   ```python
   yield table(
       data=[{"col1": "val1", "col2": "val2"}, ...],
       name="Table Name",
       description="Table description"
   ).model_dump()
   ```

### Code Style

- Follow PEP 8
- Use type hints
- Document with docstrings
- Keep functions focused and modular

## Troubleshooting

### Common Issues

**Agent not starting**:
- Check OPENAI_API_KEY is set
- Verify dependencies are installed: `pip list | grep openbb-ai`
- Check port 7777 is available: `lsof -i :7777`

**Widget data not loading**:
- Verify widget UUID format
- Check widget parameters are valid
- Review reasoning steps in response

**Tests failing**:
- Ensure test payloads are valid JSON
- Check FastAPI dependencies are installed
- Verify pytest and pytest-asyncio versions

**Import errors**:
- Run setup script: `./setup.sh`
- Manually install: `pip install -r requirements.txt`

## Dependencies

Core dependencies (see `requirements.txt`):
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sse-starlette` - Server-Sent Events
- `openbb-ai` - OpenBB integration
- `openai` - LLM integration
- `python-dotenv` - Environment management

## Credits

- Built on [agents-for-openbb](https://github.com/OpenBB-finance/agents-for-openbb)
- Integrated with [OpenBB Platform](https://openbb.co)

## License

Part of the A-LOG research framework.
