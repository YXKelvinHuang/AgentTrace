"""
Unified Log Viewer for A-LOG

This module provides tools to view all three A-LOG surfaces together:
- Operational (from JSONL and/or Jaeger)
- Cognitive (from JSONL and/or Jaeger)
- Contextual (from Jaeger only)

Usage:
    from alog.unified_viewer import UnifiedViewer

    viewer = UnifiedViewer(logs_dir="logs", jaeger_url="http://localhost:16686")
    viewer.show_all_logs()
"""

import json
import os
import requests
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict


class UnifiedViewer:
    """
    View all A-LOG data from both JSONL files and Jaeger/OpenTelemetry.
    """

    def __init__(self, logs_dir: str = "logs", jaeger_url: str = "http://localhost:16686"):
        """
        Initialize unified viewer.

        Args:
            logs_dir: Directory containing JSONL log files
            jaeger_url: Jaeger UI base URL
        """
        self.logs_dir = logs_dir
        self.jaeger_url = jaeger_url.rstrip('/')
        self.jaeger_api = f"{self.jaeger_url}/api"

    def _read_jsonl(self, filename: str) -> List[Dict[str, Any]]:
        """Read a JSONL file and return list of log entries."""
        filepath = os.path.join(self.logs_dir, filename)
        logs = []

        if not os.path.exists(filepath):
            return logs

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        logs.append(json.loads(line))
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

        return logs

    def get_jsonl_logs(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all logs from JSONL files.

        Returns:
            Dictionary with 'operational' and 'cognitive' log lists
        """
        return {
            'operational': self._read_jsonl('operational.jsonl'),
            'cognitive': self._read_jsonl('cognitive.jsonl')
        }

    def get_jaeger_traces(self, service_name: str = "A-LOG-Agent",
                          limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get traces from Jaeger API.

        Args:
            service_name: Service name to filter
            limit: Maximum number of traces to retrieve

        Returns:
            List of trace objects
        """
        try:
            # Query Jaeger API for traces
            url = f"{self.jaeger_api}/traces"
            params = {
                'service': service_name,
                'limit': limit
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            return data.get('data', [])

        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not fetch from Jaeger ({e})")
            print(f"Make sure Jaeger is running at {self.jaeger_url}")
            return []
        except Exception as e:
            print(f"Error querying Jaeger: {e}")
            return []

    def extract_contextual_from_traces(self, traces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract contextual logs from Jaeger traces.

        Args:
            traces: List of Jaeger trace objects

        Returns:
            List of contextual log entries
        """
        contextual_logs = []

        for trace in traces:
            for span in trace.get('spans', []):
                # Get tags as dict
                tags = {tag['key']: tag['value'] for tag in span.get('tags', [])}

                # Check if this is a contextual span
                if tags.get('surface') == 'contextual':
                    contextual_log = {
                        'id': span.get('spanID'),
                        'timestamp': datetime.fromtimestamp(
                            span.get('startTime', 0) / 1_000_000
                        ).isoformat(),
                        'agent': tags.get('agent', 'unknown'),
                        'surface': 'contextual',
                        'trace_id': span.get('traceID'),
                        'span_id': span.get('spanID'),
                        'event': {
                            'operation': tags.get('operation'),
                            'source_type': tags.get('source_type'),
                            'source_name': tags.get('source_name'),
                            'query': tags.get('query'),
                            'retrieved_count': int(tags.get('retrieved_count', 0)) if tags.get('retrieved_count') else None,
                            'cache_hit': tags.get('cache_hit') == 'true' if 'cache_hit' in tags else None,
                            'write_value': tags.get('write_value'),
                            'memory_state_hash': tags.get('memory_state_hash'),
                            'metadata': self._extract_metadata(tags)
                        }
                    }
                    contextual_logs.append(contextual_log)

        return contextual_logs

    def _extract_metadata(self, tags: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata fields from span tags."""
        metadata_keys = ['cache_size', 'memory_size', 'response_size']
        metadata = {}

        for key in metadata_keys:
            if key in tags:
                try:
                    metadata[key] = int(tags[key])
                except (ValueError, TypeError):
                    metadata[key] = tags[key]

        return metadata if metadata else None

    def get_all_logs(self, service_name: str = "A-LOG-Agent") -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all logs from both JSONL files and Jaeger.

        Args:
            service_name: Jaeger service name to filter

        Returns:
            Dictionary with 'operational', 'cognitive', and 'contextual' log lists
        """
        # Get JSONL logs
        logs = self.get_jsonl_logs()

        # Get Jaeger traces
        traces = self.get_jaeger_traces(service_name)

        # Extract contextual logs from traces
        logs['contextual'] = self.extract_contextual_from_traces(traces)

        return logs

    def show_all_logs(self, service_name: str = "A-LOG-Agent", format: str = "summary"):
        """
        Display all logs in a formatted view.

        Args:
            service_name: Jaeger service name to filter
            format: Display format ('summary', 'detailed', or 'json')
        """
        logs = self.get_all_logs(service_name)

        print("=" * 80)
        print("A-LOG Unified View - All Surfaces")
        print("=" * 80)

        # Summary counts
        print(f"\n📊 Log Counts:")
        print(f"  Operational: {len(logs['operational'])} events")
        print(f"  Cognitive:   {len(logs['cognitive'])} events")
        print(f"  Contextual:  {len(logs['contextual'])} events")
        print(f"  Total:       {sum(len(v) for v in logs.values())} events")

        if format == "json":
            print("\n" + json.dumps(logs, indent=2))
            return

        # Group by trace_id for correlated view
        trace_groups = defaultdict(lambda: {'operational': [], 'cognitive': [], 'contextual': []})

        for surface, events in logs.items():
            for event in events:
                trace_id = event.get('trace_id', 'no-trace')
                trace_groups[trace_id][surface].append(event)

        print(f"\n🔗 Traces: {len(trace_groups)}")

        if format == "summary":
            self._print_summary(trace_groups)
        elif format == "detailed":
            self._print_detailed(trace_groups)

    def _print_summary(self, trace_groups: Dict[str, Dict[str, List]]):
        """Print summary view of logs grouped by trace."""
        for trace_id, surfaces in list(trace_groups.items())[:10]:  # Show first 10 traces
            total_events = sum(len(events) for events in surfaces.values())
            if total_events == 0:
                continue

            print(f"\n📍 Trace: {trace_id[:16]}...")
            print(f"   Events: {surfaces['operational'].__len__()} operational, "
                  f"{surfaces['cognitive'].__len__()} cognitive, "
                  f"{surfaces['contextual'].__len__()} contextual")

            # Show first event of each type
            for surface in ['operational', 'cognitive', 'contextual']:
                if surfaces[surface]:
                    event = surfaces[surface][0]
                    timestamp = event.get('timestamp', '')[:19]
                    agent = event.get('agent', 'unknown')

                    if surface == 'operational':
                        method = event.get('event', {}).get('method', 'unknown')
                        status = event.get('event', {}).get('status', 'unknown')
                        print(f"   • [{surface}] {agent}.{method} [{status}] @ {timestamp}")

                    elif surface == 'cognitive':
                        thought = event.get('event', {}).get('thought', '')[:50]
                        print(f"   • [{surface}] {agent} - {thought}... @ {timestamp}")

                    elif surface == 'contextual':
                        operation = event.get('event', {}).get('operation', 'unknown')
                        source_type = event.get('event', {}).get('source_type', 'unknown')
                        print(f"   • [{surface}] {agent} {operation} from {source_type} @ {timestamp}")

    def _print_detailed(self, trace_groups: Dict[str, Dict[str, List]]):
        """Print detailed view of logs grouped by trace."""
        for trace_id, surfaces in list(trace_groups.items())[:5]:  # Show first 5 traces
            total_events = sum(len(events) for events in surfaces.values())
            if total_events == 0:
                continue

            print(f"\n{'=' * 80}")
            print(f"Trace: {trace_id}")
            print(f"{'=' * 80}")

            # Combine all events and sort by timestamp
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
                    print(f"Method: {event_data.get('method')}")
                    print(f"Status: {event_data.get('status')}")
                    if event_data.get('duration_sec'):
                        print(f"Duration: {event_data['duration_sec']:.3f}s")
                    if event_data.get('error'):
                        print(f"Error: {event_data['error']}")

                elif surface == 'cognitive':
                    print(f"Thought: {event_data.get('thought', '')[:100]}...")
                    if event_data.get('goal'):
                        print(f"Goal: {event_data['goal']}")

                elif surface == 'contextual':
                    print(f"Operation: {event_data.get('operation')}")
                    print(f"Source: {event_data.get('source_type')} / {event_data.get('source_name')}")
                    if event_data.get('query'):
                        print(f"Query: {event_data['query']}")
                    if event_data.get('cache_hit') is not None:
                        print(f"Cache Hit: {event_data['cache_hit']}")
                    if event_data.get('retrieved_count'):
                        print(f"Retrieved: {event_data['retrieved_count']} items")

    def export_unified_jsonl(self, output_file: str = "logs/unified.jsonl",
                            service_name: str = "A-LOG-Agent"):
        """
        Export all logs to a single unified JSONL file.

        Args:
            output_file: Output file path
            service_name: Jaeger service name to filter
        """
        logs = self.get_all_logs(service_name)

        # Combine all logs
        all_logs = []
        for surface, events in logs.items():
            all_logs.extend(events)

        # Sort by timestamp
        all_logs.sort(key=lambda x: x.get('timestamp', ''))

        # Write to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for log in all_logs:
                f.write(json.dumps(log, ensure_ascii=False) + '\n')

        print(f"✓ Exported {len(all_logs)} unified logs to {output_file}")


def view_all(logs_dir: str = "logs", jaeger_url: str = "http://localhost:16686",
             format: str = "summary"):
    """
    Quick function to view all logs.

    Args:
        logs_dir: Directory containing JSONL files
        jaeger_url: Jaeger UI URL
        format: Display format ('summary', 'detailed', or 'json')
    """
    viewer = UnifiedViewer(logs_dir, jaeger_url)
    viewer.show_all_logs(format=format)


def export_unified(logs_dir: str = "logs", jaeger_url: str = "http://localhost:16686",
                   output_file: str = "logs/unified.jsonl"):
    """
    Quick function to export unified logs.

    Args:
        logs_dir: Directory containing JSONL files
        jaeger_url: Jaeger UI URL
        output_file: Output file path
    """
    viewer = UnifiedViewer(logs_dir, jaeger_url)
    viewer.export_unified_jsonl(output_file)


if __name__ == "__main__":
    # CLI interface
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "export":
        export_unified()
    else:
        view_all(format="detailed" if "--detailed" in sys.argv else "summary")
