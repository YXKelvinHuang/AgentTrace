"""
Test Agent for Reasoning Trace Extraction

This agent demonstrates the A-LOG reasoning trace extraction functionality
by returning outputs that contain reasoning traces with the special markers.
"""

import time
import random
from typing import Any, Dict, List


class ReasoningTestAgent:
    """
    A test agent that returns outputs with embedded reasoning traces.
    
    This agent demonstrates how A-LOG can extract reasoning traces
    from LLM outputs without modifying the agent's logic.
    """
    
    def __init__(self, name: str = "ReasoningTestAgent"):
        self.name = name
        self.reasoning_count = 0
    
    def solve_problem(self, problem: str) -> str:
        """
        Solve a problem and return the answer with embedded reasoning trace.
        
        Args:
            problem: The problem to solve
            
        Returns:
            Answer with embedded reasoning trace
        """
        print(f"Solving problem: {problem}")
        
        # Simulate some processing time
        time.sleep(0.3)
        
        # Generate a reasoning trace
        self.reasoning_count += 1
        reasoning = f"""
Step {self.reasoning_count}: Analyzing the problem
- Problem type: {random.choice(['mathematical', 'logical', 'analytical'])}
- Complexity: {random.choice(['low', 'medium', 'high'])}
- Approach: {random.choice(['direct calculation', 'pattern recognition', 'systematic analysis'])}

Step {self.reasoning_count + 1}: Applying solution strategy
- Breaking down the problem into components
- Identifying key variables and relationships
- Working through the solution step by step

Step {self.reasoning_count + 2}: Verifying the result
- Checking calculations
- Validating the approach
- Confirming the answer makes sense
"""
        
        # Generate the main answer
        if "calculate" in problem.lower() or "math" in problem.lower():
            answer = "The answer is 42."
        elif "analyze" in problem.lower():
            answer = "Based on the analysis, the conclusion is X."
        else:
            answer = f"The solution to '{problem}' is: {random.choice(['Option A', 'Option B', 'Option C'])}"
        
        # Combine answer with reasoning trace
        full_output = f"""{answer}

===REASONING_TRACE_START==={reasoning}===REASONING_TRACE_END==="""
        
        return full_output
    
    def think_through(self, question: str) -> str:
        """
        Think through a question and return reasoning with trace.
        
        Args:
            question: The question to think about
            
        Returns:
            Response with embedded reasoning trace
        """
        print(f"Thinking about: {question}")
        time.sleep(0.2)
        
        reasoning = f"""
Initial thoughts on: {question}
- Understanding the context
- Identifying key concepts
- Considering multiple perspectives
- Weighing pros and cons
- Reaching a conclusion
"""
        
        response = f"My analysis suggests that the best approach is to consider all factors carefully."
        
        return f"""{response}

===REASONING_TRACE_START==={reasoning}===REASONING_TRACE_END==="""
    
    def plan_action(self, goal: str) -> str:
        """
        Plan an action with detailed reasoning.
        
        Args:
            goal: The goal to plan for
            
        Returns:
            Plan with embedded reasoning trace
        """
        print(f"Planning for goal: {goal}")
        time.sleep(0.4)
        
        reasoning = f"""
Planning process for: {goal}
1. Define success criteria
2. Identify required resources
3. Consider potential obstacles
4. Develop contingency plans
5. Create timeline and milestones
6. Validate the plan
"""
        
        plan = f"Here's the plan to achieve '{goal}': Step 1, Step 2, Step 3, Done."
        
        return f"""{plan}

===REASONING_TRACE_START==={reasoning}===REASONING_TRACE_END==="""
    
    def simple_method(self, input_data: str) -> str:
        """
        A simple method that doesn't use reasoning traces.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Simple response without reasoning trace
        """
        print(f"Processing: {input_data}")
        time.sleep(0.1)
        return f"Processed: {input_data}"
