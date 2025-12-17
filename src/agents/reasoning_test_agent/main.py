#!/usr/bin/env python3
"""
Reasoning Trace Extraction Test

This script demonstrates A-LOG's ability to extract reasoning traces
from agent outputs without modifying the agent's logic.
"""

import sys
import os
import json
from pathlib import Path

# Add the src directory to the path so we can import alog
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from alog.auto import init, instrument_agent
from agent import ReasoningTestAgent


def main():
    """Test reasoning trace extraction."""
    print("=" * 60)
    print("A-LOG Reasoning Trace Extraction Test")
    print("=" * 60)
    
    # Step 1: Initialize A-LOG
    print("\n1. Initializing A-LOG...")
    init(output_dir="logs", level="INFO")
    print("✓ A-LOG initialized")
    
    # Step 2: Create and instrument the agent
    print("\n2. Creating and instrumenting reasoning test agent...")
    agent = ReasoningTestAgent(name="ReasoningAgent")
    
    # This is the magic line - instrument the agent
    agent = instrument_agent(agent, name="ReasoningAgent")
    print("✓ Agent instrumented with A-LOG")
    
    # Step 3: Test reasoning trace extraction
    print("\n3. Testing reasoning trace extraction...")
    print("-" * 40)
    
    try:
        # Test 1: Problem solving with reasoning trace
        print("\n🧠 Test 1: Problem Solving")
        result1 = agent.solve_problem("Calculate the area of a circle with radius 5")
        print(f"Main Output: {result1}")
        
        # Test 2: Thinking through a question
        print("\n🤔 Test 2: Thinking Through")
        result2 = agent.think_through("What are the implications of AI in healthcare?")
        print(f"Main Output: {result2}")
        
        # Test 3: Planning an action
        print("\n📋 Test 3: Planning Action")
        result3 = agent.plan_action("Launch a new product")
        print(f"Main Output: {result3}")
        
        # Test 4: Simple method (no reasoning trace)
        print("\n⚡ Test 4: Simple Method")
        result4 = agent.simple_method("Hello World")
        print(f"Output: {result4}")
        
    except Exception as e:
        print(f"Error during execution: {e}")
    
    print("-" * 40)
    print("✓ Agent execution completed")
    
    # Step 4: Display the extracted reasoning traces
    print("\n4. Extracted Reasoning Traces:")
    print("-" * 40)
    
    if os.path.exists("logs/cognitive.jsonl"):
        print("\n📄 Cognitive Logs (Reasoning Traces):")
        print("-" * 20)
        
        with open("logs/cognitive.jsonl", 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                try:
                    log_entry = json.loads(line.strip())
                    event = log_entry.get('event', {})
                    thought = event.get('thought', '')
                    goal = event.get('goal', '')
                    
                    print(f"\n{i}. {goal}")
                    print(f"   Thought: {thought[:100]}{'...' if len(thought) > 100 else ''}")
                except json.JSONDecodeError:
                    print(f"{i}. (Invalid JSON)")
    else:
        print("\n📄 No cognitive logs found")
    
    # Step 5: Show operational logs
    print("\n5. Operational Logs:")
    print("-" * 40)
    
    if os.path.exists("logs/operational.jsonl"):
        print("\n📄 Operational Events:")
        print("-" * 20)
        
        with open("logs/operational.jsonl", 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[-5:], 1):  # Show last 5 entries
                try:
                    log_entry = json.loads(line.strip())
                    event = log_entry.get('event', {})
                    method = event.get('method', 'unknown')
                    status = event.get('status', 'unknown')
                    duration = event.get('duration_sec', 0)
                    
                    if duration is not None:
                        print(f"{i}. {method} - {status} ({duration:.3f}s)")
                    else:
                        print(f"{i}. {method} - {status}")
                except json.JSONDecodeError:
                    print(f"{i}. (Invalid JSON)")
    
    # Step 6: Show statistics
    print("\n6. A-LOG Statistics:")
    print("-" * 40)
    
    try:
        from alog.core import ALogger
        logger = ALogger("logs")
        stats = logger.get_stats()
        
        print(f"Total events logged: {stats['total_events']}")
        print(f"  - Operational: {stats['operational_events']}")
        print(f"  - Cognitive: {stats['cognitive_events']}")
        print("  - Contextual: OTel-only (not stored in files)")

    except Exception as e:
        print(f"Could not retrieve statistics: {e}")
    
    print("\n" + "=" * 60)
    print("Reasoning Trace Extraction Test Complete!")
    print("Check the 'logs/' directory for detailed JSON logs.")
    print("=" * 60)


if __name__ == "__main__":
    main()
