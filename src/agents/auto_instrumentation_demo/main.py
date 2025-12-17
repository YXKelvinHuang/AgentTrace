#!/usr/bin/env python3
"""
A-LOG Auto-Instrumentation Demonstration

This demonstrates the CORRECT way to capture contextual logs:
AUTOMATIC instrumentation via OpenTelemetry - NO manual logging needed!

Run this with:
    ALOG_ENABLE_OTEL=true python src/agents/auto_instrumentation_demo/main.py

Then view traces in Jaeger:
    open http://localhost:16686

You'll see:
- Operational logs: Method calls (run_workflow, process_data, etc.)
- Contextual logs: HTTP calls AUTOMATICALLY captured (GitHub API, JSONPlaceholder, etc.)
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from alog.auto import init, instrument_agent
from agent import AutoInstrumentedAgent


def main():
    """Main demonstration function."""
    print("=" * 70)
    print("A-LOG Auto-Instrumentation Demonstration")
    print("=" * 70)

    # Check if OTel is enabled
    otel_enabled = os.getenv('ALOG_ENABLE_OTEL', 'false').lower() in ('true', '1', 'yes')

    if not otel_enabled:
        print("\n⚠️  WARNING: OpenTelemetry is NOT enabled!")
        print("   Auto-instrumentation requires OTel to be enabled.")
        print("\n   To see automatic contextual logging:")
        print("   1. Start Jaeger:  ./scripts/start_jaeger.sh")
        print("   2. Run with:      ALOG_ENABLE_OTEL=true python src/agents/auto_instrumentation_demo/main.py")
        print("   3. View traces:   open http://localhost:16686")
        print("\n   Continuing anyway (only operational logs will be captured)...\n")

    # Step 1: Initialize A-LOG with auto-instrumentation
    print("\n1. Initializing A-LOG with auto-instrumentation...")
    print("-" * 70)
    init(output_dir="logs", level="INFO", auto_instrument=True)
    print("-" * 70)
    print("✓ A-LOG initialized")

    if otel_enabled:
        print("\n💡 Key Point:")
        print("   HTTP libraries (requests, urllib3) are now auto-instrumented.")
        print("   Every HTTP call will be AUTOMATICALLY logged as a contextual event.")
        print("   NO manual record_contextual() calls needed!")

    # Step 2: Create and instrument the agent
    print("\n2. Creating and instrumenting agent...")
    agent = AutoInstrumentedAgent(name="AutoAgent")
    agent = instrument_agent(agent, name="AutoAgent")
    print("✓ Agent instrumented with A-LOG")

    # Step 3: Run the agent - HTTP calls are AUTOMATICALLY logged
    print("\n3. Running agent workflow...")
    print("   Watch for HTTP calls - they're automatically captured by OTel!")
    print("-" * 70)

    try:
        result = agent.run_workflow()
        print(f"\nResult: {result}")
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()

    # Step 4: Summary
    print("\n4. What Just Happened:")
    print("=" * 70)

    print("\n📊 Operational Logs (Method Calls):")
    print("  - logs/operational.jsonl contains:")
    print("    • run_workflow [start/complete]")
    print("    • process_data [start/complete]")
    print("    • fetch_multiple_apis [start/complete]")
    print("    • fetch_github_user [start/complete]")

    if otel_enabled:
        print("\n🌐 Contextual Logs (HTTP Calls) - AUTOMATICALLY CAPTURED:")
        print("  - OTel captured (NO manual logging):")
        print("    • GET https://api.github.com/users/octocat")
        print("    • GET https://jsonplaceholder.typicode.com/posts/1")
        print("    • GET https://api.github.com/users/torvalds")
        print("\n  Each HTTP span includes:")
        print("    • Full URL and method")
        print("    • HTTP status code")
        print("    • Request/response headers")
        print("    • Duration")
        print("    • Response size")

        print("\n🔭 View in Jaeger:")
        print("  1. Open: http://localhost:16686")
        print("  2. Service: A-LOG-Agent")
        print("  3. Find your trace")
        print("  4. Expand to see:")
        print("     - Operational spans (method calls)")
        print("     - Contextual spans (HTTP calls) ← AUTOMATICALLY CAPTURED")
        print("\n  You'll see a beautiful timeline showing:")
        print("     • Which methods called which APIs")
        print("     • How long each API call took")
        print("     • The full request/response details")
        print("     • Correlated by trace ID")

    else:
        print("\n❌ Contextual Logs NOT Captured:")
        print("  - OTel is disabled")
        print("  - HTTP calls were made but not logged")
        print("  - Enable OTel to see automatic contextual logging")

    print("\n" + "=" * 70)
    print("Auto-Instrumentation Demonstration Complete!")
    print("\nKey Takeaway:")
    print("  Contextual logs are AUTOMATIC when using instrumented libraries.")
    print("  No manual record_contextual() calls needed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
