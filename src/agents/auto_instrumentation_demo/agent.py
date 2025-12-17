"""
Auto-Instrumentation Demo Agent

This agent makes REAL HTTP calls to demonstrate OpenTelemetry auto-instrumentation.
NO MANUAL LOGGING - contextual logs are automatically captured by OTel!
"""

import requests
import time
from typing import Dict, Any, List


class AutoInstrumentedAgent:
    """
    An agent that uses instrumented libraries.

    When OTel is enabled, all HTTP calls are AUTOMATICALLY logged as contextual events.
    No manual record_contextual() calls needed!
    """

    def __init__(self, name: str = "AutoAgent"):
        self.name = name

    def fetch_github_user(self, username: str) -> Dict[str, Any]:
        """
        Fetch GitHub user data via HTTP.

        With OTel auto-instrumentation enabled, this HTTP call is AUTOMATICALLY
        captured as a contextual log with all details (URL, status, duration, etc.)
        """
        print(f"Fetching GitHub user: {username}")

        # This HTTP call is AUTOMATICALLY instrumented by OTel
        # NO manual logging needed!
        response = requests.get(f"https://api.github.com/users/{username}")

        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Found user: {data.get('name', username)}")
            return data
        else:
            print(f"  ✗ Failed: {response.status_code}")
            return {}

    def fetch_multiple_apis(self) -> List[Dict[str, Any]]:
        """
        Call multiple APIs to demonstrate automatic contextual logging.

        Each HTTP call is automatically logged with:
        - URL
        - Method
        - Status code
        - Duration
        - Headers
        - Response size
        """
        results = []

        # Call 1: GitHub API
        print("\n1. Calling GitHub API...")
        results.append(self.fetch_github_user("octocat"))

        time.sleep(0.5)

        # Call 2: JSONPlaceholder API
        print("\n2. Calling JSONPlaceholder API...")
        response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
        if response.status_code == 200:
            results.append(response.json())
            print(f"  ✓ Got post: {response.json().get('title', 'N/A')[:50]}...")

        time.sleep(0.5)

        # Call 3: Another GitHub call
        print("\n3. Calling GitHub API again...")
        results.append(self.fetch_github_user("torvalds"))

        return results

    def process_data(self, data: str) -> str:
        """
        Simple processing method.
        This shows operational logging (method calls) vs contextual (HTTP calls).
        """
        print(f"Processing: {data}")
        time.sleep(0.2)
        return f"Processed: {data}"

    def run_workflow(self) -> Dict[str, Any]:
        """
        Run a workflow that combines operational and contextual logging.

        Operational logs: method calls, timing, errors
        Contextual logs: HTTP calls (automatically captured by OTel)
        """
        print(f"\n{'='*60}")
        print(f"{self.name} starting workflow...")
        print(f"{'='*60}")

        # Operational log: This method call is logged
        self.process_data("initialization")

        # Contextual logs: These HTTP calls are AUTOMATICALLY logged
        api_results = self.fetch_multiple_apis()

        # Operational log: This method call is logged
        summary = self.process_data(f"fetched {len(api_results)} API results")

        print(f"\n{'='*60}")
        print(f"Workflow complete!")
        print(f"{'='*60}")

        return {
            "api_calls": len(api_results),
            "summary": summary
        }
