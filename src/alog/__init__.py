"""
A-LOG: Structured Logging for Agent Observability

Core module for structured, schema-based logging and benchmarking
of LLM-based agents using OpenTelemetry and LogBench.

Main exports:
- init(): Initialize the global A-LOG logger
- instrument_agent(): Wrap an agent with automatic logging
- ALogger: Core logging class
"""

from .auto import init, instrument_agent
from .core import ALogger

__all__ = ['init', 'instrument_agent', 'ALogger']
