#!/usr/bin/env python3
"""
A-LOG Unified Log Viewer CLI

View all A-LOG surfaces (operational, cognitive, contextual) in one place.

Usage:
    python scripts/view_logs.py                    # Summary view
    python scripts/view_logs.py --detailed         # Detailed view
    python scripts/view_logs.py --export unified.jsonl  # Export to single file
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alog.core import ALogger
import json
from datetime import datetime
from collections import defaultdict


def view_logs_simple(logs_dir="logs"):
    """Simple viewer that reads all JSONL files."""
    logger = ALogger(logs_dir, save_contextual_to_file=True)

    print("=" * 80)
    print("A-LOG Unified View - All Three Surfaces")
    print("=" * 80)

    # Get all logs
    operational = logger.get_logs("operational")
    cognitive = logger.get_logs("cognitive")
    contextual = logger.get_logs("contextual")

    print(f"\n📊 Log Counts:")
    print(f"  Operational: {len(operational)} events")
    print(f"  Cognitive:   {len(cognitive)} events")
    print(f"  Contextual:  {len(contextual)} events")
    print(f"  Total:       {len(operational) + len(cognitive) + len(contextual)} events")

    # Group by trace
    trace_groups = defaultdict(lambda: {'operational': [], 'cognitive': [], 'contextual': []})

    for log in operational:
        trace_id = log.get('trace_id', 'no-trace')
        trace_groups[trace_id]['operational'].append(log)

    for log in cognitive:
        trace_id = log.get('trace_id', 'no-trace')
        trace_groups[trace_id]['cognitive'].append(log)

    for log in contextual:
        trace_id = log.get('trace_id', 'no-trace')
        trace_groups[trace_id]['contextual'].append(log)

    print(f"\n🔗 Traces: {len(trace_groups)}")

    return trace_groups


def print_summary(trace_groups):
    """Print summary of traces."""
    print("\n" + "=" * 80)
    print("Trace Summary")
    print("=" * 80)

    for i, (trace_id, surfaces) in enumerate(list(trace_groups.items())[:10], 1):
        total_events = sum(len(events) for events in surfaces.values())
        if total_events == 0:
            continue

        print(f"\n📍 Trace #{i}: {trace_id[:16]}...")
        print(f"   Events: {len(surfaces['operational'])} operational, "
              f"{len(surfaces['cognitive'])} cognitive, "
              f"{len(surfaces['contextual'])} contextual")

        # Show timeline
        all_events = []
        for surface, events in surfaces.items():
            for event in events:
                event['_surface'] = surface
                all_events.append(event)

        all_events.sort(key=lambda x: x.get('timestamp', ''))

        for event in all_events[:5]:  # Show first 5 events
            surface = event['_surface']
            timestamp = event.get('timestamp', '')[:19]
            agent = event.get('agent', 'unknown')
            event_data = event.get('event', {})

            if surface == 'operational':
                method = event_data.get('method', 'unknown')
                status = event_data.get('status', 'unknown')
                duration = event_data.get('duration_sec')
                duration_str = f" ({duration:.3f}s)" if duration else ""
                print(f"   • {timestamp} [{surface:12s}] {agent}.{method} [{status}]{duration_str}")

            elif surface == 'cognitive':
                thought = event_data.get('thought', '')[:40]
                print(f"   • {timestamp} [{surface:12s}] {agent} - {thought}...")

            elif surface == 'contextual':
                operation = event_data.get('operation', 'unknown')
                source_type = event_data.get('source_type', 'unknown')
                cache_hit = event_data.get('cache_hit')
                cache_str = f" [cache {'HIT' if cache_hit else 'MISS'}]" if cache_hit is not None else ""
                print(f"   • {timestamp} [{surface:12s}] {agent} {operation} from {source_type}{cache_str}")


def print_detailed(trace_groups):
    """Print detailed view of traces."""
    for i, (trace_id, surfaces) in enumerate(list(trace_groups.items())[:5], 1):
        total_events = sum(len(events) for events in surfaces.values())
        if total_events == 0:
            continue

        print(f"\n{'=' * 80}")
        print(f"Trace #{i}: {trace_id}")
        print(f"{'=' * 80}")

        # Combine and sort all events
        all_events = []
        for surface, events in surfaces.items():
            for event in events:
                event['_surface'] = surface
                all_events.append(event)

        all_events.sort(key=lambda x: x.get('timestamp', ''))

        for event in all_events:
            surface = event['_surface']
            timestamp = event.get('timestamp', '')[:19]
            agent = event.get('agent', 'unknown')
            event_data = event.get('event', {})

            print(f"\n[{surface.upper()}] {timestamp}")
            print(f"Agent: {agent}")

            if surface == 'operational':
                print(f"  Method: {event_data.get('method')}")
                print(f"  Status: {event_data.get('status')}")
                if event_data.get('duration_sec'):
                    print(f"  Duration: {event_data['duration_sec']:.3f}s")
                if event_data.get('error'):
                    print(f"  Error: {event_data['error']}")

            elif surface == 'cognitive':
                thought = event_data.get('thought', '')
                print(f"  Thought: {thought[:100]}...")
                if event_data.get('goal'):
                    print(f"  Goal: {event_data['goal']}")

            elif surface == 'contextual':
                print(f"  Operation: {event_data.get('operation')}")
                print(f"  Source: {event_data.get('source_type')} / {event_data.get('source_name')}")
                if event_data.get('query'):
                    print(f"  Query: {event_data['query']}")
                if event_data.get('cache_hit') is not None:
                    print(f"  Cache Hit: {event_data['cache_hit']}")
                if event_data.get('retrieved_count'):
                    print(f"  Retrieved: {event_data['retrieved_count']} items")


def export_unified(logs_dir="logs", output_file="unified.jsonl"):
    """Export all logs to a single file."""
    logger = ALogger(logs_dir, save_contextual_to_file=True)

    # Get all logs
    all_logs = []
    all_logs.extend(logger.get_logs("operational"))
    all_logs.extend(logger.get_logs("cognitive"))
    all_logs.extend(logger.get_logs("contextual"))

    # Sort by timestamp
    all_logs.sort(key=lambda x: x.get('timestamp', ''))

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        for log in all_logs:
            f.write(json.dumps(log, ensure_ascii=False) + '\n')

    print(f"✓ Exported {len(all_logs)} unified logs to {output_file}")


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    logs_dir = "logs"

    # Check if logs directory exists
    if not os.path.exists(logs_dir):
        print(f"Error: Log directory '{logs_dir}' not found.")
        print("Run an instrumented agent first to generate logs.")
        return

    # Export mode
    if "--export" in sys.argv:
        idx = sys.argv.index("--export")
        output_file = sys.argv[idx + 1] if len(sys.argv) > idx + 1 else "unified.jsonl"
        export_unified(logs_dir, output_file)
        return

    # View mode
    trace_groups = view_logs_simple(logs_dir)

    if "--detailed" in sys.argv:
        print_detailed(trace_groups)
    else:
        print_summary(trace_groups)

    print("\n" + "=" * 80)
    print("💡 Tips:")
    print("  --detailed       Show detailed view with all event data")
    print("  --export FILE    Export all logs to a single unified JSONL file")
    print("=" * 80)


if __name__ == "__main__":
    main()
