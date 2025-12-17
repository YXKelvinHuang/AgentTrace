#!/usr/bin/env python3
"""
A-LOG Example Demonstration

This script demonstrates the A-LOG instrumentation system by:
1. Creating an example agent
2. Instrumenting it with A-LOG
3. Running the agent and observing the automatic logging
4. Displaying the generated logs

Run this script to see A-LOG in action:
    python src/agents/example_agent/main.py
"""

import sys
import os
import json
from pathlib import Path

# Add the src directory to the path so we can import alog
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from alog.auto import init, instrument_agent
from agent import ExampleAgent


def main():
    """Main demonstration function."""
    print("=" * 60)
    print("A-LOG Demonstration")
    print("=" * 60)
    
    # Step 1: Initialize A-LOG
    print("\n1. Initializing A-LOG...")
    init(output_dir="logs", level="INFO")
    print("✓ A-LOG initialized")
    
    # Step 2: Create and instrument the agent
    print("\n2. Creating and instrumenting agent...")
    agent = ExampleAgent(name="DemoAgent")
    
    # This is the magic line - instrument the agent
    agent = instrument_agent(agent, name="DemoAgent")
    print("✓ Agent instrumented with A-LOG")
    
    # Step 3: Run the agent normally
    print("\n3. Running agent tasks...")
    print("-" * 40)
    
    # Run various agent methods
    try:
        # Main execution
        result1 = agent.run("Calculate the sum of numbers")
        print(f"Result 1: {result1}")
        
        # Another execution
        result2 = agent.run("Search for information about AI")
        print(f"Result 2: {result2}")
        
        # Learning
        agent.learn("Successfully completed a calculation task")
        
        # Training
        training_data = ["example1", "example2", "example3"]
        training_result = agent.train(training_data)
        print(f"Training result: {training_result}")
        
        # Tool execution
        tool_result = agent.execute_tool("calculator", {"operation": "add", "values": [5, 10, 15]})
        print(f"Tool result: {tool_result}")
        
        # Cognitive methods
        thoughts = agent.think("How can I improve my performance?")
        print(f"Thoughts: {thoughts}")
        
        reasoning = agent.reason("The current approach seems inefficient")
        print(f"Reasoning: {reasoning}")
        
    except Exception as e:
        print(f"Error during execution: {e}")
    
    print("-" * 40)
    print("✓ Agent execution completed")
    
    # Step 4: Display the generated logs
    print("\n4. Generated A-LOG files:")
    print("-" * 40)

    # Note: Contextual logs are OTel-only and don't produce a JSONL file
    log_files = ["logs/operational.jsonl", "logs/cognitive.jsonl"]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📄 {log_file}:")
            print("-" * 20)
            
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[-3:], 1):  # Show last 3 entries
                    try:
                        log_entry = json.loads(line.strip())
                        surface = log_entry.get('surface', 'unknown')
                        agent = log_entry.get('agent', 'unknown')
                        event = log_entry.get('event', {})

                        # Extract event-specific fields
                        if surface == 'operational':
                            method = event.get('method', 'unknown')
                            status = event.get('status', 'unknown')
                            print(f"{i}. {surface} - {agent}.{method} [{status}]")
                            duration = event.get('duration_sec')
                            if duration:
                                print(f"   Duration: {duration:.3f}s")
                        elif surface == 'cognitive':
                            thought = event.get('thought', '')
                            thought_preview = thought[:50] + '...' if len(thought) > 50 else thought
                            print(f"{i}. {surface} - {agent}")
                            print(f"   Thought: {thought_preview}")
                        else:
                            print(f"{i}. {surface} - {agent}")
                    except json.JSONDecodeError:
                        print(f"{i}. (Invalid JSON)")
        else:
            print(f"\n📄 {log_file}: (File not found)")
    
    # Step 5: Show statistics
    print("\n5. A-LOG Statistics:")
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
    print("A-LOG Demonstration Complete!")
    print("Check the 'logs/' directory for detailed JSON logs.")
    print("=" * 60)


if __name__ == "__main__":
    main()
