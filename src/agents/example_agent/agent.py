"""
Example Agent for A-LOG Demonstration

This is a simple agent that demonstrates the A-LOG instrumentation system.
It has methods that will be automatically detected and instrumented.
"""

import time
import random
from typing import Any, Dict, List


class ExampleAgent:
    """
    A simple example agent with various methods that A-LOG can instrument.
    
    This agent demonstrates:
    - Main execution methods (run, execute)
    - Learning methods (learn, train)
    - Tool methods (execute_tool)
    - Cognitive methods (think, reason)
    """
    
    def __init__(self, name: str = "ExampleAgent"):
        self.name = name
        self.knowledge = []
        self.tools = ["calculator", "web_search", "database"]
    
    def run(self, task: str) -> str:
        """
        Main execution method - processes a task.
        
        Args:
            task: The task to process
            
        Returns:
            Result of the task processing
        """
        print(f"Agent {self.name} is running task: {task}")
        
        # Simulate some processing time
        time.sleep(0.5)
        
        # Think about the task
        reasoning = self.think(task)
        
        # Execute the task
        result = self.execute(task, reasoning)
        
        return f"Completed task '{task}' with result: {result}"
    
    def execute(self, task: str, reasoning: str = None) -> str:
        """
        Execute a specific task.
        
        Args:
            task: The task to execute
            reasoning: Optional reasoning for the task
            
        Returns:
            Execution result
        """
        print(f"Executing: {task}")
        if reasoning:
            print(f"Reasoning: {reasoning}")
        
        # Simulate execution
        time.sleep(0.3)
        
        # Simulate different types of results
        if "calculate" in task.lower():
            return self.execute_tool("calculator", {"operation": "add", "values": [1, 2, 3]})
        elif "search" in task.lower():
            return self.execute_tool("web_search", {"query": task})
        else:
            return f"Processed: {task}"
    
    def think(self, problem: str) -> str:
        """
        Cognitive method - think about a problem.
        
        Args:
            problem: The problem to think about
            
        Returns:
            Reasoning or thoughts
        """
        print(f"Thinking about: {problem}")
        
        # Simulate thinking time
        time.sleep(0.2)
        
        thoughts = [
            f"I need to analyze this problem: {problem}",
            "Let me break this down into steps",
            "I should consider multiple approaches",
            "Based on my knowledge, I think the best approach is..."
        ]
        
        return random.choice(thoughts)
    
    def reason(self, situation: str) -> str:
        """
        Another cognitive method - reason about a situation.
        
        Args:
            situation: The situation to reason about
            
        Returns:
            Reasoning result
        """
        print(f"Reasoning about: {situation}")
        time.sleep(0.1)
        
        return f"After careful consideration of {situation}, I conclude that..."
    
    def learn(self, experience: str) -> None:
        """
        Learning method - learn from experience.
        
        Args:
            experience: The experience to learn from
        """
        print(f"Learning from: {experience}")
        
        # Simulate learning time
        time.sleep(0.4)
        
        # Add to knowledge base
        self.knowledge.append(experience)
        print(f"Knowledge base now has {len(self.knowledge)} items")
    
    def train(self, data: List[str]) -> Dict[str, Any]:
        """
        Training method - train on data.
        
        Args:
            data: Training data
            
        Returns:
            Training results
        """
        print(f"Training on {len(data)} data points")
        
        # Simulate training time
        time.sleep(1.0)
        
        # Simulate training results
        accuracy = random.uniform(0.7, 0.95)
        loss = random.uniform(0.1, 0.5)
        
        return {
            "accuracy": accuracy,
            "loss": loss,
            "epochs": 10,
            "data_points": len(data)
        }
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """
        Tool execution method - execute a specific tool.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Tool execution result
        """
        print(f"Executing tool: {tool_name} with parameters: {parameters}")
        
        # Simulate tool execution time
        time.sleep(0.2)
        
        if tool_name == "calculator":
            if "operation" in parameters and "values" in parameters:
                if parameters["operation"] == "add":
                    result = sum(parameters["values"])
                    return f"Addition result: {result}"
        
        elif tool_name == "web_search":
            query = parameters.get("query", "")
            return f"Search results for '{query}': Found 5 relevant pages"
        
        elif tool_name == "database":
            return "Database query executed successfully"
        
        return f"Tool {tool_name} executed with result: success"
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status (not instrumented - doesn't match target patterns).
        
        Returns:
            Current status information
        """
        return {
            "name": self.name,
            "knowledge_items": len(self.knowledge),
            "available_tools": self.tools,
            "status": "active"
        }
