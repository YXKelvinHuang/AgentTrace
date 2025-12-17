"""
OpenTelemetry Auto-Instrumentation for A-LOG

This module automatically instruments common libraries to capture contextual logs
without manual logging. When enabled, A-LOG will automatically capture:

- HTTP/API calls (requests, urllib3, httpx)
- Database queries (SQLAlchemy, Redis, MongoDB)
- Vector store operations (if instrumented)
- Cache operations
- Any library with OTel instrumentation

This is the CORRECT way to get contextual logs - automatic capture via OTel,
not manual record_contextual() calls.
"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def enable_auto_instrumentation(libraries: Optional[List[str]] = None) -> List[str]:
    """
    Enable OpenTelemetry auto-instrumentation for common libraries.

    This automatically captures contextual logs (API calls, DB queries, etc.)
    without requiring manual logging in your agent code.

    Args:
        libraries: List of libraries to instrument. If None, instruments all available.
                  Options: 'requests', 'urllib3', 'httpx', 'sqlalchemy', 'redis', 'pymongo'

    Returns:
        List of successfully instrumented libraries

    Example:
        from alog.auto_instrument import enable_auto_instrumentation

        # Instrument everything
        enable_auto_instrumentation()

        # Or specific libraries
        enable_auto_instrumentation(['requests', 'redis'])
    """
    instrumented = []

    # Default to all if not specified
    if libraries is None:
        libraries = ['requests', 'urllib3', 'httpx', 'sqlalchemy', 'redis', 'pymongo']

    # Instrument HTTP libraries
    if 'requests' in libraries:
        try:
            from opentelemetry.instrumentation.requests import RequestsInstrumentor
            RequestsInstrumentor().instrument()
            instrumented.append('requests')
            logger.info("✓ Auto-instrumented: requests (HTTP calls)")
        except ImportError:
            logger.debug("requests instrumentation not available (install: opentelemetry-instrumentation-requests)")
        except Exception as e:
            logger.warning(f"Failed to instrument requests: {e}")

    if 'urllib3' in libraries:
        try:
            from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
            URLLib3Instrumentor().instrument()
            instrumented.append('urllib3')
            logger.info("✓ Auto-instrumented: urllib3 (HTTP calls)")
        except ImportError:
            logger.debug("urllib3 instrumentation not available (install: opentelemetry-instrumentation-urllib3)")
        except Exception as e:
            logger.warning(f"Failed to instrument urllib3: {e}")

    if 'httpx' in libraries:
        try:
            from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
            HTTPXClientInstrumentor().instrument()
            instrumented.append('httpx')
            logger.info("✓ Auto-instrumented: httpx (HTTP calls)")
        except ImportError:
            logger.debug("httpx instrumentation not available (install: opentelemetry-instrumentation-httpx)")
        except Exception as e:
            logger.warning(f"Failed to instrument httpx: {e}")

    # Instrument database libraries
    if 'sqlalchemy' in libraries:
        try:
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
            SQLAlchemyInstrumentor().instrument()
            instrumented.append('sqlalchemy')
            logger.info("✓ Auto-instrumented: sqlalchemy (SQL queries)")
        except ImportError:
            logger.debug("sqlalchemy instrumentation not available (install: opentelemetry-instrumentation-sqlalchemy)")
        except Exception as e:
            logger.warning(f"Failed to instrument sqlalchemy: {e}")

    if 'redis' in libraries:
        try:
            from opentelemetry.instrumentation.redis import RedisInstrumentor
            RedisInstrumentor().instrument()
            instrumented.append('redis')
            logger.info("✓ Auto-instrumented: redis (cache operations)")
        except ImportError:
            logger.debug("redis instrumentation not available (install: opentelemetry-instrumentation-redis)")
        except Exception as e:
            logger.warning(f"Failed to instrument redis: {e}")

    if 'pymongo' in libraries:
        try:
            from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
            PymongoInstrumentor().instrument()
            instrumented.append('pymongo')
            logger.info("✓ Auto-instrumented: pymongo (MongoDB operations)")
        except ImportError:
            logger.debug("pymongo instrumentation not available (install: opentelemetry-instrumentation-pymongo)")
        except Exception as e:
            logger.warning(f"Failed to instrument pymongo: {e}")

    if instrumented:
        logger.info(f"Auto-instrumentation enabled for: {', '.join(instrumented)}")
    else:
        logger.warning("No libraries were auto-instrumented. Install OTel instrumentation packages.")

    return instrumented


def disable_auto_instrumentation(libraries: Optional[List[str]] = None):
    """
    Disable OpenTelemetry auto-instrumentation.

    Args:
        libraries: List of libraries to un-instrument. If None, un-instruments all.
    """
    if libraries is None:
        libraries = ['requests', 'urllib3', 'httpx', 'sqlalchemy', 'redis', 'pymongo']

    # Un-instrument HTTP libraries
    if 'requests' in libraries:
        try:
            from opentelemetry.instrumentation.requests import RequestsInstrumentor
            RequestsInstrumentor().uninstrument()
            logger.info("✓ Un-instrumented: requests")
        except Exception as e:
            logger.debug(f"Failed to un-instrument requests: {e}")

    if 'urllib3' in libraries:
        try:
            from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
            URLLib3Instrumentor().uninstrument()
            logger.info("✓ Un-instrumented: urllib3")
        except Exception as e:
            logger.debug(f"Failed to un-instrument urllib3: {e}")

    if 'httpx' in libraries:
        try:
            from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
            HTTPXClientInstrumentor().uninstrument()
            logger.info("✓ Un-instrumented: httpx")
        except Exception as e:
            logger.debug(f"Failed to un-instrument httpx: {e}")

    # Un-instrument database libraries
    if 'sqlalchemy' in libraries:
        try:
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
            SQLAlchemyInstrumentor().uninstrument()
            logger.info("✓ Un-instrumented: sqlalchemy")
        except Exception as e:
            logger.debug(f"Failed to un-instrument sqlalchemy: {e}")

    if 'redis' in libraries:
        try:
            from opentelemetry.instrumentation.redis import RedisInstrumentor
            RedisInstrumentor().uninstrument()
            logger.info("✓ Un-instrumented: redis")
        except Exception as e:
            logger.debug(f"Failed to un-instrument redis: {e}")

    if 'pymongo' in libraries:
        try:
            from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
            PymongoInstrumentor().uninstrument()
            logger.info("✓ Un-instrumented: pymongo")
        except Exception as e:
            logger.debug(f"Failed to un-instrument pymongo: {e}")


__all__ = ['enable_auto_instrumentation', 'disable_auto_instrumentation']
