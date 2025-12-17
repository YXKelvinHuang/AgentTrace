"""
Exporter modules for different logging backends.

This module provides exporters for A-LOG data to various formats and backends:
- JSONL: Line-delimited JSON files (default format)
- SQLite: Relational database for querying and analysis
- OTLP: OpenTelemetry Protocol for distributed tracing
"""

import json
import sqlite3
import os
from typing import Any, Dict, List, Optional
from datetime import datetime


class JSONLExporter:
    """
    Export A-LOG events to JSONL (JSON Lines) format.
    This is the default exporter used by ALogger.
    """

    def __init__(self, output_dir: str = "logs"):
        """
        Initialize JSONL exporter.

        Args:
            output_dir: Directory to store JSONL files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.operational_file = os.path.join(output_dir, "operational.jsonl")
        self.cognitive_file = os.path.join(output_dir, "cognitive.jsonl")

    def export(self, surface: str, log_entry: Dict[str, Any]) -> None:
        """
        Export a log entry to the appropriate JSONL file.

        Args:
            surface: Log surface (operational, cognitive)
            log_entry: The structured log entry
        """
        if surface == "operational":
            filepath = self.operational_file
        elif surface == "cognitive":
            filepath = self.cognitive_file
        else:
            # Contextual events don't get exported to JSONL
            return

        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Failed to export to {filepath}: {e}")

    def read(self, surface: str) -> List[Dict[str, Any]]:
        """
        Read log entries from a JSONL file.

        Args:
            surface: Log surface to read (operational, cognitive)

        Returns:
            List of log entries
        """
        if surface == "operational":
            filepath = self.operational_file
        elif surface == "cognitive":
            filepath = self.cognitive_file
        else:
            return []

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
            print(f"Failed to read {filepath}: {e}")

        return logs


class SQLiteExporter:
    """
    Export A-LOG events to SQLite database for structured querying.
    Useful for complex analysis and filtering of log data.
    """

    def __init__(self, db_path: str = "logs/alog.db"):
        """
        Initialize SQLite exporter.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Operational events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operational (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                agent TEXT NOT NULL,
                surface TEXT NOT NULL,
                level TEXT NOT NULL,
                trace_id TEXT,
                span_id TEXT,
                method TEXT,
                status TEXT,
                duration_sec REAL,
                tool_name TEXT,
                result_summary TEXT,
                error TEXT,
                metadata TEXT
            )
        """)

        # Cognitive events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cognitive (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                agent TEXT NOT NULL,
                surface TEXT NOT NULL,
                level TEXT NOT NULL,
                trace_id TEXT,
                span_id TEXT,
                reasoning_step INTEGER,
                thought TEXT,
                plan TEXT,
                reflection TEXT,
                confidence REAL,
                goal TEXT,
                model TEXT,
                token_count INTEGER
            )
        """)

        # Contextual events table (for OTel data if persisted)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contextual (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                agent TEXT NOT NULL,
                surface TEXT NOT NULL,
                level TEXT NOT NULL,
                trace_id TEXT,
                span_id TEXT,
                operation TEXT,
                source_type TEXT,
                source_name TEXT,
                query TEXT,
                retrieved_count INTEGER,
                cache_hit INTEGER,
                metadata TEXT
            )
        """)

        conn.commit()
        conn.close()

    def export(self, surface: str, log_entry: Dict[str, Any]) -> None:
        """
        Export a log entry to SQLite database.

        Args:
            surface: Log surface (operational, cognitive, contextual)
            log_entry: The structured log entry
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if surface == "operational":
                event = log_entry.get("event", {})
                cursor.execute("""
                    INSERT INTO operational
                    (id, timestamp, agent, surface, level, trace_id, span_id,
                     method, status, duration_sec, tool_name, result_summary, error, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_entry.get("id"),
                    log_entry.get("timestamp"),
                    log_entry.get("agent"),
                    log_entry.get("surface"),
                    log_entry.get("level"),
                    log_entry.get("trace_id"),
                    log_entry.get("span_id"),
                    event.get("method"),
                    event.get("status"),
                    event.get("duration_sec"),
                    event.get("tool_name"),
                    event.get("result_summary"),
                    event.get("error"),
                    json.dumps(event.get("metadata", {}))
                ))

            elif surface == "cognitive":
                event = log_entry.get("event", {})
                cursor.execute("""
                    INSERT INTO cognitive
                    (id, timestamp, agent, surface, level, trace_id, span_id,
                     reasoning_step, thought, plan, reflection, confidence, goal, model, token_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_entry.get("id"),
                    log_entry.get("timestamp"),
                    log_entry.get("agent"),
                    log_entry.get("surface"),
                    log_entry.get("level"),
                    log_entry.get("trace_id"),
                    log_entry.get("span_id"),
                    event.get("reasoning_step"),
                    event.get("thought"),
                    event.get("plan"),
                    event.get("reflection"),
                    event.get("confidence"),
                    event.get("goal"),
                    event.get("model"),
                    event.get("token_count")
                ))

            elif surface == "contextual":
                event = log_entry.get("event", {})
                cursor.execute("""
                    INSERT INTO contextual
                    (id, timestamp, agent, surface, level, trace_id, span_id,
                     operation, source_type, source_name, query, retrieved_count, cache_hit, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_entry.get("id"),
                    log_entry.get("timestamp"),
                    log_entry.get("agent"),
                    log_entry.get("surface"),
                    log_entry.get("level"),
                    log_entry.get("trace_id"),
                    log_entry.get("span_id"),
                    event.get("operation"),
                    event.get("source_type"),
                    event.get("source_name"),
                    event.get("query"),
                    event.get("retrieved_count"),
                    1 if event.get("cache_hit") else 0,
                    json.dumps(event.get("metadata", {}))
                ))

            conn.commit()
        except Exception as e:
            print(f"Failed to export to SQLite: {e}")
        finally:
            conn.close()

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            List of result rows as dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except Exception as e:
            print(f"Query failed: {e}")
            return []
        finally:
            conn.close()


class OTLPExporter:
    """
    Export A-LOG events using OpenTelemetry Protocol (OTLP).
    This is a wrapper around the OTelExporter for consistency.
    """

    def __init__(self, service_name: str = "A-LOG", endpoint: str = "http://localhost:4317"):
        """
        Initialize OTLP exporter.

        Args:
            service_name: Service name for OpenTelemetry
            endpoint: OTLP collector endpoint
        """
        from ..otel_exporter import OTelExporter
        self.exporter = OTelExporter(service_name=service_name, endpoint=endpoint)

    def export(self, surface: str, agent: str, event: Dict[str, Any]) -> None:
        """
        Export an event as an OTLP span.

        Args:
            surface: Log surface (operational, cognitive, contextual)
            agent: Agent name
            event: Event data
        """
        try:
            self.exporter.emit_span(surface, agent, event)
        except Exception as e:
            print(f"Failed to export via OTLP: {e}")


__all__ = ['JSONLExporter', 'SQLiteExporter', 'OTLPExporter']
