#!/usr/bin/env python3
"""
A-LOG Contextual Logging Demonstration

This script demonstrates the contextual logging surface of A-LOG by:
1. Setting up an agent with various data operations
2. Instrumenting it with A-LOG
3. Performing operations that generate contextual logs
4. Showing how to view the data in Jaeger

Run this script with OpenTelemetry enabled:
    ALOG_ENABLE_OTEL=true python src/agents/contextual_demo/main.py

Or start Jaeger first:
    ./scripts/start_jaeger.sh
    ALOG_ENABLE_OTEL=true python src/agents/contextual_demo/main.py
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from alog.auto import init, instrument_agent
from agent import ContextualDemoAgent


def main():
    """Main demonstration function."""
    print("=" * 70)
    print("A-LOG Contextual Logging Demonstration")
    print("=" * 70)

    # Check if OTel is enabled
    otel_enabled = os.getenv('ALOG_ENABLE_OTEL', 'false').lower() in ('true', '1', 'yes')

    if not otel_enabled:
        print("\n💡 Note: OpenTelemetry is disabled")
        print("   Contextual logs will be saved to logs/contextual.jsonl")
        print("   To also send to Jaeger for visual traces:")
        print("   1. Start Jaeger:  ./scripts/start_jaeger.sh")
        print("   2. Run with:      ALOG_ENABLE_OTEL=true python src/agents/contextual_demo/main.py")
        print("\n   Continuing with local file logging...\n")

    # Step 1: Initialize A-LOG
    print("\n1. Initializing A-LOG...")
    init(output_dir="logs", level="INFO")
    print("✓ A-LOG initialized")

    if otel_enabled:
        print("✓ OpenTelemetry enabled - contextual logs will be sent to Jaeger")
        print("  View traces at: http://localhost:16686")

    # Step 2: Create and instrument the agent
    print("\n2. Creating and instrumenting contextual demo agent...")
    agent = ContextualDemoAgent(name="ContextualAgent")

    # Instrument the agent
    agent = instrument_agent(agent, name="ContextualAgent")
    print("✓ Agent instrumented with A-LOG")

    # Step 3: Run operations that generate contextual logs
    print("\n3. Running operations with contextual logging...")
    print("=" * 70)

    try:
        # Operation 1: Search vector database
        print("\n🔍 Operation 1: Vector Database Search")
        print("-" * 40)
        agent.search_vector_db("AI in healthcare", top_k=2)

        # Operation 2: Cache retrieval (miss)
        print("\n💾 Operation 2: Cache Retrieval (miss)")
        print("-" * 40)
        agent.retrieve_from_cache("nonexistent_key")

        # Operation 3: Memory storage
        print("\n🧠 Operation 3: Memory Storage")
        print("-" * 40)
        agent.store_in_memory("user_preference", {"theme": "dark", "language": "en"})

        # Operation 4: External API call
        print("\n🌐 Operation 4: External API Call")
        print("-" * 40)
        agent.call_external_api("/api/v1/analyze", {"query": "test", "mode": "fast"})

        # Operation 5: Complex workflow with multiple contextual operations
        print("\n🔄 Operation 5: Complex Workflow")
        print("-" * 40)
        result = agent.process_with_context("Analyze healthcare AI trends")
        print(f"Result: {result}")

        # Operation 6: Cache retrieval (hit)
        print("\n✅ Operation 6: Cache Retrieval (hit)")
        print("-" * 40)
        cached = agent.retrieve_from_cache("task:Analyze healthcare AI trends")
        print(f"Retrieved: {cached}")

    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("✓ Operations completed")

    # Step 4: Summary
    print("\n4. Summary and Next Steps:")
    print("=" * 70)

    print("\n📊 Log Files Generated:")
    print("  - logs/operational.jsonl (method calls, timing)")
    print("  - logs/cognitive.jsonl (reasoning traces, if any)")
    print("  - logs/contextual.jsonl (data retrieval, cache, APIs)")

    print("\n🔍 View All Logs Together:")
    print("  python scripts/view_logs.py")

    if otel_enabled:
        print("\n🔭 OpenTelemetry Traces (Also sent to Jaeger):")
        print("  - Open Jaeger UI: http://localhost:16686")
        print("  - Service: A-LOG-Agent")
        print("  - Look for 'ContextualAgent.contextual' spans")
        print("\n  In Jaeger you can:")
        print("    • View the full trace timeline")
        print("    • See contextual operations (retrieve, store)")
        print("    • Inspect span attributes (cache_hit, source_type, etc.)")
        print("    • Correlate operational and contextual events")
    else:
        print("\n💾 Local Files Only (OTel Disabled):")
        print("  - All logs saved to JSONL files")
        print("  - No Docker/Jaeger required")
        print("  - Full visibility in local files")

    print("\n" + "=" * 70)
    print("Contextual Logging Demonstration Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
