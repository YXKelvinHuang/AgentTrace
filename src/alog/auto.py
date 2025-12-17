"""
A-LOG Auto Instrumentation Module

This module provides the main interface for automatically instrumenting agents
with structured logging capabilities. It implements the runtime observer pattern
where A-LOG wraps agent methods without modifying the original agent code.

Key Functions:
- init(): Initialize the global A-LOG logger
- instrument_agent(): Wrap an agent with automatic logging
"""

import inspect
import functools
import time
import json
import os
import re
from typing import Any, Dict, List, Optional, Callable, Tuple
from datetime import datetime, timezone
import logging

from .core import ALogger


# Global logger instance
_global_logger: Optional[ALogger] = None

# Reasoning trace markers
TRACE_START = "===REASONING_TRACE_START==="
TRACE_END = "===REASONING_TRACE_END==="


def _extract_reasoning_trace(output: str) -> Tuple[str, Optional[str]]:
    """
    Extract reasoning trace from the model output while preserving the main answer.
    
    Args:
        output: The full output string from the agent
        
    Returns:
        Tuple of (main_output, reasoning_trace)
    """
    if not isinstance(output, str):
        return output, None

    pattern = re.compile(
        rf"{re.escape(TRACE_START)}(.*?){re.escape(TRACE_END)}",
        flags=re.DOTALL
    )
    match = pattern.search(output)
    if not match:
        return output.strip(), None

    reasoning = match.group(1).strip()
    main_output = (output[:match.start()] + output[match.end():]).strip()
    return main_output, reasoning


def init(output_dir: str = "logs", level: str = "INFO",
         enable_otel: bool = None, otel_endpoint: str = "http://localhost:4317",
         save_contextual_to_file: bool = False,
         auto_instrument: bool = True) -> None:
    """
    Initialize the global A-LOG logger.

    Args:
        output_dir: Directory to store log files
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_otel: Enable OpenTelemetry export. If None, checks ALOG_ENABLE_OTEL env var
        otel_endpoint: OpenTelemetry collector endpoint
        save_contextual_to_file: Save contextual logs to JSONL (for offline analysis)
        auto_instrument: Auto-instrument common libraries (requests, redis, etc.) for contextual logs
    """
    global _global_logger

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Check environment variable if enable_otel not explicitly set
    if enable_otel is None:
        enable_otel = os.getenv('ALOG_ENABLE_OTEL', 'false').lower() in ('true', '1', 'yes')

    # Check for custom endpoint from environment
    otel_endpoint = os.getenv('ALOG_OTEL_ENDPOINT', otel_endpoint)

    # Enable auto-instrumentation if OTel is enabled
    if enable_otel and auto_instrument:
        from .auto_instrument import enable_auto_instrumentation
        instrumented = enable_auto_instrumentation()
        if instrumented:
            print(f"  Auto-instrumented: {', '.join(instrumented)}")
            print(f"    → Contextual logs will be automatically captured from these libraries")

    # Initialize the global logger
    _global_logger = ALogger(
        output_dir=output_dir,
        level=level,
        enable_otel=enable_otel,
        otel_endpoint=otel_endpoint,
        save_contextual_to_file=save_contextual_to_file
    )

    print(f"A-LOG initialized: logging to {output_dir}/")
    if enable_otel:
        print(f"  OpenTelemetry: enabled → {otel_endpoint}")
        print(f"  Contextual logs: Automatically captured via OTel instrumentation")
    else:
        print(f"  OpenTelemetry: disabled (set ALOG_ENABLE_OTEL=true to enable)")
        print(f"  Contextual logs: Not captured (OTel required for auto-instrumentation)")

    if save_contextual_to_file:
        print(f"  Contextual logs also saved to: {output_dir}/contextual.jsonl")


def instrument_agent(agent: Any, name: str, methods: Optional[List[str]] = None) -> Any:
    """
    Instrument an agent with automatic logging.

    Args:
        agent: The agent object to instrument
        name: Name identifier for the agent
        methods: Optional list of specific method names to wrap.
                 If None, all callable public methods will be wrapped.

    Returns:
        The instrumented agent (same object, methods replaced)
    """
    global _global_logger

    if _global_logger is None:
        raise RuntimeError("A-LOG not initialized. Call init() first.")

    # Identify target methods
    if methods is None:
        target_methods = [
            attr for attr in dir(agent)
            if not attr.startswith("_")
            and callable(getattr(agent, attr))
        ]
    else:
        target_methods = [
            m for m in methods
            if hasattr(agent, m) and callable(getattr(agent, m))
        ]

    if not target_methods:
        print(f"No valid methods found to instrument on {name}")
        return agent

    # Dynamic wrapping
    for method_name in target_methods:
        original_method = getattr(agent, method_name)
        wrapped_method = _create_logged_wrapper(original_method, name, method_name)
        setattr(agent, method_name, wrapped_method)

    print(f"Agent '{name}' instrumented with {len(target_methods)} methods: {target_methods}")
    return agent


# Note: legacy target-method identification helpers removed in favor of
# an explicit optional methods parameter and default public-callables discovery.


def _create_logged_wrapper(original_method: Callable, agent_name: str, method_name: str) -> Callable:
    """
    Create a wrapper function that logs method execution.
    
    Args:
        original_method: The original method to wrap
        agent_name: Name of the agent
        method_name: Name of the method
        
    Returns:
        Wrapped method with logging
    """
    @functools.wraps(original_method)
    def logged_wrapper(*args, **kwargs):
        global _global_logger
        
        start_time = time.time()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Log start event
        _global_logger.record_operational(
            agent=agent_name,
            method=method_name,
            status="start",
            metadata={
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys()) if kwargs else []
            }
        )
        
        try:
            # Execute the original method
            result = original_method(*args, **kwargs)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log completion
            _global_logger.record_operational(
                agent=agent_name,
                method=method_name,
                status="complete",
                duration_sec=duration,
                result_summary=str(result)[:100] + "..." if result and len(str(result)) > 100 else str(result),
                metadata={
                    "result_type": type(result).__name__ if result is not None else "None"
                }
            )
            
            # If result contains reasoning or text, extract and log reasoning trace
            if result is not None and isinstance(result, str):
                # Extract reasoning trace if present
                main_output, reasoning = _extract_reasoning_trace(result)

                # Log cognitive reasoning trace separately if found
                if reasoning:
                    _global_logger.record_cognitive(
                        agent=agent_name,
                        thought=reasoning,
                        goal=f"Execute {method_name}",
                        model="agent_method"
                    )
                    # Only replace result if reasoning was actually extracted
                    # This preserves original output when no reasoning markers are present
                    result = main_output
            
            return result
            
        except Exception as e:
            # Calculate duration even for errors
            duration = time.time() - start_time

            # Build detailed error message
            error_message = f"{type(e).__name__}: {str(e)}"

            # Log error with full context
            _global_logger.record_operational(
                agent=agent_name,
                method=method_name,
                status="error",
                duration_sec=duration,
                error=error_message,
                metadata={
                    "error_type": type(e).__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()) if kwargs else []
                },
                level="ERROR"
            )

            # Re-raise the exception to preserve original behavior
            raise
    
    return logged_wrapper
