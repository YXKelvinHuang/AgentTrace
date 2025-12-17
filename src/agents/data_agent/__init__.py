"""
Data Agent: A versatile multi-task agent built on the Adala framework.

This agent provides various data processing capabilities:
- Summarization: Condense long texts
- Question Answering: Answer questions with optional context
- Entity Extraction: Extract named entities from text
- Classification: Categorize text into predefined labels
- Sentiment Analysis: Analyze text sentiment
- Text Generation: Generate new text from prompts
- Custom Pipelines: Chain multiple skills together

Example usage:
    >>> from agents.data_agent import DataAgent
    >>>
    >>> # Create agent
    >>> agent = DataAgent(model='gpt-4o')
    >>>
    >>> # Summarize text
    >>> result = agent.summarize("Long text here...")
    >>>
    >>> # Answer questions
    >>> result = agent.answer_question("What is AI?")
    >>>
    >>> # Classify text
    >>> result = agent.classify("Text to classify", labels=['tech', 'business', 'science'])
    >>>
    >>> # Analyze sentiment
    >>> result = agent.analyze_sentiment("This is amazing!")
"""

from .main import DataAgent

__all__ = ['DataAgent']
__version__ = '0.2.0'
