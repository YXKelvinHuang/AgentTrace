"""
Financial Agent: A comprehensive OpenBB-integrated agent.

This agent combines multiple features from the agents-for-openbb repository:
- Widget data retrieval and integration
- Reasoning steps for transparency
- Citations for data attribution
- Charts and visualizations
- Tables for structured data display
"""

import os
from pathlib import Path
from typing import AsyncGenerator, Optional, List, Dict, Any
from dotenv import load_dotenv

# FastAPI and SSE
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sse_starlette import EventSourceResponse

# OpenAI for LLM
import openai
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
)

# OpenBB AI SDK
from openbb_ai import (
    QueryRequest,
    message_chunk,
    reasoning_step,
    chart,
    table,
    citations,
    cite,
    get_widget_data,
    WidgetRequest,
)


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Financial Agent",
    description="A comprehensive financial analysis agent with OpenBB integration",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Financial Agent",
        "version": "1.0.0",
        "status": "running",
        "description": "OpenBB-integrated financial agent"
    }


@app.get("/agents.json")
async def get_agents():
    """
    Agent registration endpoint for OpenBB Workspace.

    Defines agent capabilities and features:
    - streaming: Real-time SSE responses
    - widget-dashboard-select: Widget selector UI
    - widget-dashboard-search: Dashboard widget discovery
    """
    return JSONResponse({
        "financial_agent": {
            "name": "Financial Agent",
            "description": "Comprehensive financial analysis agent with widget integration, visualizations, and citations",
            "image": "https://openbb.co/assets/images/openbb-logo.png",
            "endpoints": {
                "query": "/v1/query"
            },
            "features": {
                "streaming": True,
                "widget-dashboard-select": True,
                "widget-dashboard-search": True,
                "enable-charts": {
                    "label": "Enable Charts",
                    "default": True,
                    "description": "Generate visualizations from financial data"
                },
                "enable-tables": {
                    "label": "Enable Tables",
                    "default": True,
                    "description": "Display structured data tables"
                },
                "enable-citations": {
                    "label": "Enable Citations",
                    "default": True,
                    "description": "Show data source citations"
                }
            }
        }
    })


@app.post("/v1/query")
async def query(request: QueryRequest) -> EventSourceResponse:
    """
    Main query endpoint for processing user requests.

    This endpoint:
    1. Checks if widget data needs to be retrieved
    2. Processes conversation history
    3. Generates responses with reasoning steps, charts, tables, and citations
    4. Streams results via Server-Sent Events

    Args:
        request: QueryRequest containing messages, widgets, workspace state

    Returns:
        EventSourceResponse with streaming SSE events
    """

    # Extract workspace options (feature toggles)
    workspace_options = getattr(request, "workspace_options", []) or []
    enable_charts = "enable-charts" in workspace_options
    enable_tables = "enable-tables" in workspace_options
    enable_citations = "enable-citations" in workspace_options

    # Check if we need to retrieve widget data
    last_message = request.messages[-1] if request.messages else None

    if (last_message and
        last_message.role == "human" and
        request.widgets and
        request.widgets.primary):

        # Early exit to fetch widget data
        async def retrieve_widget_data() -> AsyncGenerator[Dict[str, Any], None]:
            yield reasoning_step(
                event_type="INFO",
                message=f"Retrieving data from {len(request.widgets.primary)} selected widget(s)..."
            ).model_dump()

            # Create widget requests
            widget_requests = []
            for widget in request.widgets.primary:
                widget_requests.append(WidgetRequest(
                    widget=widget,
                    input_arguments={
                        param.name: param.current_value
                        for param in widget.params
                    }
                ))

            # Request widget data
            yield get_widget_data(widget_requests).model_dump()

        return EventSourceResponse(
            content=retrieve_widget_data(),
            media_type="text/event-stream"
        )

    # Main execution loop
    async def execution_loop() -> AsyncGenerator[Dict[str, Any], None]:
        try:
            # Convert messages to OpenAI format
            openai_messages = []
            widget_context = ""
            citation_data = []

            # System message
            system_prompt = """You are a financial analysis expert integrated with OpenBB Workspace.

Your capabilities:
- Analyze financial data from widgets (stocks, options, fundamentals, etc.)
- Generate insights and actionable recommendations
- Create visualizations (charts) and structured tables
- Provide data citations for transparency

When analyzing data:
1. Be concise and data-driven
2. Highlight key insights and trends
3. Use specific numbers and percentages
4. Suggest relevant follow-up analyses

Always maintain professional financial analysis standards."""

            openai_messages.append(
                ChatCompletionSystemMessageParam(
                    role="system",
                    content=system_prompt
                )
            )

            # Process conversation history
            for index, message in enumerate(request.messages):
                if message.role == "human":
                    openai_messages.append(
                        ChatCompletionUserMessageParam(
                            role="user",
                            content=message.content
                        )
                    )

                elif message.role == "assistant":
                    openai_messages.append(
                        ChatCompletionAssistantMessageParam(
                            role="assistant",
                            content=message.content
                        )
                    )

                elif message.role == "tool" and index == len(request.messages) - 1:
                    # This is widget data from the last retrieval
                    context_str = "Use the following widget data to answer the question:\n\n"

                    for result in message.data:
                        context_str += f"**Widget: {result.widget_name}**\n"

                        for item in result.items:
                            context_str += f"{item.content}\n\n"

                            # Store for citations
                            if enable_citations and request.widgets and request.widgets.primary:
                                matching_widgets = [
                                    w for w in request.widgets.primary
                                    if w.name == result.widget_name
                                ]
                                if matching_widgets:
                                    citation_data.append({
                                        "widget": matching_widgets[0],
                                        "content": item.content[:200]
                                    })

                    widget_context = context_str

                    # Append context to last user message
                    if openai_messages and openai_messages[-1]["role"] == "user":
                        openai_messages[-1]["content"] += f"\n\n{widget_context}"

            # Reasoning step: Starting analysis
            yield reasoning_step(
                event_type="INFO",
                message="Starting financial analysis..."
            ).model_dump()

            # Call LLM
            client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response_text = ""
            async for event in await client.chat.completions.create(
                model="gpt-4o",
                messages=openai_messages,
                temperature=0.7,
                stream=True
            ):
                if event.choices and event.choices[0].delta.content:
                    chunk = event.choices[0].delta.content
                    response_text += chunk
                    yield message_chunk(chunk).model_dump()

            # Generate example chart if enabled and we have widget data
            if enable_charts and widget_context:
                yield reasoning_step(
                    event_type="INFO",
                    message="Generating visualization..."
                ).model_dump()

                # Example chart (in production, parse actual data)
                yield chart(
                    type="line",
                    data=[
                        {"date": "2024-01", "value": 100},
                        {"date": "2024-02", "value": 105},
                        {"date": "2024-03", "value": 103},
                        {"date": "2024-04", "value": 110},
                        {"date": "2024-05", "value": 115},
                    ],
                    x_key="date",
                    y_keys=["value"],
                    name="Financial Trend",
                    description="Example trend visualization from widget data"
                ).model_dump()

            # Generate example table if enabled and we have widget data
            if enable_tables and widget_context:
                yield table(
                    data=[
                        {"metric": "Revenue", "value": "$100M", "change": "+15%"},
                        {"metric": "Net Income", "value": "$25M", "change": "+20%"},
                        {"metric": "EPS", "value": "$2.50", "change": "+18%"},
                    ],
                    name="Key Financial Metrics",
                    description="Summary of key performance indicators"
                ).model_dump()

            # Generate citations if enabled
            if enable_citations and citation_data:
                citation_list = []
                for item in citation_data:
                    citation_list.append(cite(
                        widget=item["widget"],
                        input_arguments={
                            param.name: param.current_value
                            for param in item["widget"].params
                        },
                        extra_details={
                            "Widget Name": item["widget"].name,
                            "Preview": item["content"]
                        }
                    ))

                if citation_list:
                    yield citations(citation_list).model_dump()

        except Exception as e:
            yield reasoning_step(
                event_type="ERROR",
                message=f"Error during analysis: {str(e)}"
            ).model_dump()

    return EventSourceResponse(
        content=execution_loop(),
        media_type="text/event-stream"
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7777)
