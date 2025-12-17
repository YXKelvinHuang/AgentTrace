"""
Core module for A-LOG structured logging.

Responsibilities:
- Define the ALogger class.
- Handle structured logging to JSONL and OpenTelemetry backends.
- Support multiple logging surfaces (cognitive, operational, contextual).
- Manage log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
"""

import json
import os
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .otel_exporter import OTelExporter


class ALogger:
    """
    Core A-LOG logger for structured agent observability.
    
    This class handles the structured logging of agent activities across
    three surfaces: operational, cognitive, and contextual.
    """
    
    def __init__(self, output_dir: str = "logs", level: str = "INFO",
                 enable_otel: bool = False,
                 otel_service_name: str = "A-LOG-Agent",
                 otel_endpoint: str = "http://localhost:4317",
                 save_contextual_to_file: bool = True):
        """
        Initialize the A-LOG logger.

        Args:
            output_dir: Directory to store log files
            level: Logging level for console output
            enable_otel: Enable OpenTelemetry export
            otel_service_name: Service name for OTel
            otel_endpoint: OTel collector endpoint
            save_contextual_to_file: Also save contextual logs to JSONL (in addition to OTel)
        """
        self.output_dir = output_dir
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.save_contextual_to_file = save_contextual_to_file
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize log file handles
        # NOTE: Operational and cognitive always write to JSONL
        # Contextual writes to JSONL only if save_contextual_to_file=True
        self.operational_file = os.path.join(output_dir, "operational.jsonl")
        self.cognitive_file = os.path.join(output_dir, "cognitive.jsonl")
        self.contextual_file = os.path.join(output_dir, "contextual.jsonl") if save_contextual_to_file else None
        
        # Setup console logging
        self.console_logger = logging.getLogger("alog")
        self.console_logger.setLevel(self.level)
        
        if not self.console_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.console_logger.addHandler(handler)
        
        # Trace and span tracking
        self.current_trace_id = None
        self.current_span_id = None

        # OpenTelemetry
        self.enable_otel = enable_otel
        self.otel = OTelExporter(service_name=otel_service_name, endpoint=otel_endpoint) if enable_otel else None
    
    def record(self, surface: str, agent: str, event: Dict[str, Any], 
                level: str = "INFO", trace_id: Optional[str] = None, 
                span_id: Optional[str] = None) -> None:
        """
        Record a structured log entry with the new schema format.
        
        Args:
            surface: Log surface (operational, cognitive, contextual)
            agent: Agent name
            event: Event data specific to the surface
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            trace_id: Optional trace ID for distributed tracing
            span_id: Optional span ID for distributed tracing
        """
        # Generate IDs if not provided
        if trace_id is None:
            trace_id = self.current_trace_id or str(uuid.uuid4())
            self.current_trace_id = trace_id
        
        if span_id is None:
            span_id = str(uuid.uuid4())
        
        # Create the envelope structure
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent,
            "surface": surface,
            "level": level,
            "trace_id": trace_id,
            "span_id": span_id,
            "event": event
        }
        
        # Write to appropriate file
        # NOTE: Contextual can optionally be written to file for full local visibility
        if surface == "operational":
            self._write_to_file(self.operational_file, log_entry)
        elif surface == "cognitive":
            self._write_to_file(self.cognitive_file, log_entry)
        elif surface == "contextual":
            # Contextual logs write to file if save_contextual_to_file=True
            if self.contextual_file:
                self._write_to_file(self.contextual_file, log_entry)
        else:
            # Default to operational for unknown surfaces
            self._write_to_file(self.operational_file, log_entry)

        # Export to OpenTelemetry if enabled
        if self.enable_otel and self.otel:
            try:
                self.otel.emit_span(surface, agent, event)
            except Exception as e:
                self.console_logger.warning(f"[OTEL] Failed to emit span: {e}")
        
        # Console logging for important events
        if surface == "operational" and event.get('status') in ['start', 'complete', 'error']:
            self.console_logger.info(f"{agent}.{event.get('method', 'unknown')} - {event.get('status', 'unknown')}")
    
    def record_operational(self, agent: str, method: str, status: str, 
                          duration_sec: Optional[float] = None, tool_name: Optional[str] = None,
                          tool_parameters: Optional[Dict[str, Any]] = None,
                          result_summary: Optional[str] = None, error: Optional[str] = None,
                          token_usage: Optional[Dict[str, int]] = None,
                          latency_ms: Optional[int] = None, caller: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None,
                          level: str = "INFO", trace_id: Optional[str] = None,
                          span_id: Optional[str] = None) -> None:
        """
        Record an operational surface event.
        
        Args:
            agent: Agent name
            method: Method name being called
            status: Status (start, complete, error)
            duration_sec: Execution duration in seconds
            tool_name: Name of tool being used (if applicable)
            tool_parameters: Parameters passed to tool
            result_summary: Summary of the result
            error: Error message if status is error
            token_usage: Token usage statistics
            latency_ms: Latency in milliseconds
            caller: Name of calling agent
            metadata: Additional metadata
        """
        event = {
            "method": method,
            "status": status,
            "duration_sec": duration_sec,
            "tool_name": tool_name,
            "tool_parameters": tool_parameters,
            "result_summary": result_summary,
            "error": error,
            "token_usage": token_usage,
            "latency_ms": latency_ms,
            "caller": caller,
            "metadata": metadata or {}
        }
        
        self.record("operational", agent, event, level, trace_id, span_id)
    
    def record_cognitive(self, agent: str, thought: Optional[str] = None,
                        reasoning_step: Optional[int] = None, plan: Optional[str] = None,
                        reflection: Optional[str] = None, confidence: Optional[float] = None,
                        goal: Optional[str] = None, model: Optional[str] = None,
                        token_count: Optional[int] = None, prompt_excerpt: Optional[str] = None,
                        completion_excerpt: Optional[str] = None,
                        level: str = "INFO", trace_id: Optional[str] = None,
                        span_id: Optional[str] = None) -> None:
        """
        Record a cognitive surface event.
        
        Args:
            agent: Agent name
            thought: Current thought or reasoning
            reasoning_step: Step number in reasoning process
            plan: Plan or strategy being followed
            reflection: Reflection on previous actions
            confidence: Confidence level (0.0 to 1.0)
            goal: Current goal or objective
            model: AI model being used
            token_count: Number of tokens used
            prompt_excerpt: Excerpt of the prompt
            completion_excerpt: Excerpt of the completion
        """
        # Truncate very long reasoning traces to keep log size manageable
        if thought and len(thought) > 2000:
            thought = thought[:2000] + "..."
        
        event = {
            "reasoning_step": reasoning_step,
            "thought": thought,
            "plan": plan,
            "reflection": reflection,
            "confidence": confidence,
            "goal": goal,
            "model": model,
            "token_count": token_count,
            "prompt_excerpt": prompt_excerpt,
            "completion_excerpt": completion_excerpt
        }
        
        self.record("cognitive", agent, event, level, trace_id, span_id)
    
    def record_contextual(self, agent: str, operation: str, source_type: Optional[str] = None,
                         source_name: Optional[str] = None, query: Optional[str] = None,
                         retrieved_count: Optional[int] = None,
                         retrieved_items: Optional[List[Dict[str, Any]]] = None,
                         provenance: Optional[List[str]] = None, cache_hit: Optional[bool] = None,
                         write_value: Optional[Any] = None, memory_state_hash: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None,
                         level: str = "INFO", trace_id: Optional[str] = None,
                         span_id: Optional[str] = None) -> None:
        """
        Record a contextual surface event.
        
        Args:
            agent: Agent name
            operation: Operation being performed (retrieve, store, update, delete)
            source_type: Type of data source (vector_db, memory, api, etc.)
            source_name: Name of the data source
            query: Query used for retrieval
            retrieved_count: Number of items retrieved
            retrieved_items: List of retrieved items with scores
            provenance: List of source IDs
            cache_hit: Whether this was a cache hit
            write_value: Value being written (if applicable)
            memory_state_hash: Hash of memory state
            metadata: Additional metadata
        """
        event = {
            "operation": operation,
            "source_type": source_type,
            "source_name": source_name,
            "query": query,
            "retrieved_count": retrieved_count,
            "retrieved_items": retrieved_items,
            "provenance": provenance,
            "cache_hit": cache_hit,
            "write_value": write_value,
            "memory_state_hash": memory_state_hash,
            "metadata": metadata or {}
        }

        # Use the standard record() method which handles file writing and OTel
        self.record("contextual", agent, event, level, trace_id, span_id)
    
    def _write_to_file(self, filepath: str, log_entry: Dict[str, Any]) -> None:
        """
        Write a log entry to a JSONL file.
        
        Args:
            filepath: Path to the log file
            log_entry: Dictionary to write as JSON line
        """
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            self.console_logger.error(f"Failed to write to {filepath}: {e}")
    
    def get_logs(self, surface: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve logs from files.

        Args:
            surface: Specific surface to retrieve (operational, cognitive, contextual)
                    Note: contextual logs only in files if save_contextual_to_file=True

        Returns:
            List of log entries
        """
        logs = []

        if surface is None or surface == "operational":
            logs.extend(self._read_file(self.operational_file))
        if surface is None or surface == "cognitive":
            logs.extend(self._read_file(self.cognitive_file))
        if (surface is None or surface == "contextual") and self.contextual_file:
            logs.extend(self._read_file(self.contextual_file))

        return logs
    
    def _read_file(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Read and parse a JSONL file.
        
        Args:
            filepath: Path to the JSONL file
            
        Returns:
            List of parsed log entries
        """
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
            self.console_logger.error(f"Failed to read {filepath}: {e}")
        
        return logs
    
    def clear_logs(self) -> None:
        """
        Clear all log files.
        """
        files_to_clear = [self.operational_file, self.cognitive_file]
        if self.contextual_file:
            files_to_clear.append(self.contextual_file)

        for filepath in files_to_clear:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    self.console_logger.error(f"Failed to remove {filepath}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about logged events in JSONL files.

        Returns:
            Dictionary with log statistics
        """
        operational_logs = self._read_file(self.operational_file)
        cognitive_logs = self._read_file(self.cognitive_file)
        contextual_logs = self._read_file(self.contextual_file) if self.contextual_file else []

        stats = {
            'operational_events': len(operational_logs),
            'cognitive_events': len(cognitive_logs),
            'total_events': len(operational_logs) + len(cognitive_logs)
        }

        if self.contextual_file:
            stats['contextual_events'] = len(contextual_logs)
            stats['total_events'] += len(contextual_logs)

        return stats
