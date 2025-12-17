"""
Financial Agent: OpenBB-integrated agent.

A comprehensive financial analysis agent that combines:
- Widget data integration from OpenBB Workspace
- Real-time streaming responses
- Reasoning steps for transparency
- Charts and tables for visualization
- Citations for data attribution

Example usage:
    Run the agent server:
    >>> uvicorn main:app --host 0.0.0.0 --port 7777

    Test the agent:
    >>> pytest tests/test_agent.py -v

For detailed documentation, see README.md
"""

from .main import app

__all__ = ["app"]

__version__ = "1.0.0"
