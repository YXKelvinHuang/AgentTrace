"""
Contextual Logging Demo Agent

This agent demonstrates how to use A-LOG's contextual logging to track
data retrieval, memory operations, and external API calls.
"""

import time
import random
from typing import Any, Dict, List


class ContextualDemoAgent:
    """
    An agent that demonstrates contextual logging for data operations.

    This agent shows how to log:
    - Vector database retrievals
    - Memory operations
    - External API calls
    - Cache hits/misses
    """

    def __init__(self, name: str = "ContextualAgent"):
        self.name = name
        self.memory = {}
        self.vector_db = {
            "doc1": {"content": "AI is transforming healthcare", "embedding": [0.1, 0.2, 0.3]},
            "doc2": {"content": "Machine learning models require data", "embedding": [0.2, 0.3, 0.4]},
            "doc3": {"content": "Neural networks learn patterns", "embedding": [0.3, 0.4, 0.5]},
        }
        self.cache = {}

    def search_vector_db(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search vector database and log the retrieval with A-LOG.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of search results
        """
        print(f"Searching vector DB for: {query}")

        # Import logger to manually log contextual events
        from alog.auto import _global_logger

        # Simulate search time
        time.sleep(0.3)

        # Get results (simulated)
        results = [
            {"id": "doc1", "score": 0.95, "content": "AI is transforming healthcare"},
            {"id": "doc2", "score": 0.87, "content": "Machine learning models require data"},
        ][:top_k]

        # Log contextual event for vector DB retrieval
        if _global_logger:
            _global_logger.record_contextual(
                agent=self.name,
                operation="retrieve",
                source_type="vector_db",
                source_name="embeddings_store",
                query=query,
                retrieved_count=len(results),
                retrieved_items=results,
                provenance=["doc1", "doc2"],
                cache_hit=False
            )

        return results

    def retrieve_from_cache(self, key: str) -> Any:
        """
        Retrieve data from cache and log the operation.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        print(f"Checking cache for: {key}")

        from alog.auto import _global_logger

        time.sleep(0.1)

        # Check cache
        cache_hit = key in self.cache
        value = self.cache.get(key)

        # Log contextual event for cache retrieval
        if _global_logger:
            _global_logger.record_contextual(
                agent=self.name,
                operation="retrieve",
                source_type="cache",
                source_name="memory_cache",
                query=key,
                retrieved_count=1 if cache_hit else 0,
                cache_hit=cache_hit,
                metadata={"cache_size": len(self.cache)}
            )

        if cache_hit:
            print(f"  ✓ Cache hit: {key}")
        else:
            print(f"  ✗ Cache miss: {key}")

        return value

    def store_in_memory(self, key: str, value: Any) -> None:
        """
        Store data in memory and log the operation.

        Args:
            key: Memory key
            value: Value to store
        """
        print(f"Storing in memory: {key}")

        from alog.auto import _global_logger

        time.sleep(0.1)

        # Store in memory
        self.memory[key] = value

        # Log contextual event for memory write
        if _global_logger:
            _global_logger.record_contextual(
                agent=self.name,
                operation="store",
                source_type="memory",
                source_name="agent_memory",
                write_value=str(value)[:100],  # Truncate long values
                memory_state_hash=str(hash(str(self.memory))),
                metadata={"memory_size": len(self.memory)}
            )

        print(f"  ✓ Stored: {key}")

    def call_external_api(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call external API and log the retrieval.

        Args:
            endpoint: API endpoint
            params: API parameters

        Returns:
            API response
        """
        print(f"Calling API: {endpoint}")

        from alog.auto import _global_logger

        time.sleep(0.5)

        # Simulate API call
        response = {
            "status": "success",
            "data": {"result": "API response data here"},
            "timestamp": time.time()
        }

        # Log contextual event for API retrieval
        if _global_logger:
            _global_logger.record_contextual(
                agent=self.name,
                operation="retrieve",
                source_type="api",
                source_name=endpoint,
                query=str(params),
                retrieved_count=1,
                retrieved_items=[{"status": response["status"]}],
                cache_hit=False,
                metadata={"response_size": len(str(response))}
            )

        print(f"  ✓ API response received")
        return response

    def process_with_context(self, task: str) -> str:
        """
        Main processing method that uses multiple contextual operations.

        Args:
            task: Task to process

        Returns:
            Processing result
        """
        print(f"\nProcessing task: {task}")

        # Check cache first
        cached_result = self.retrieve_from_cache(f"task:{task}")
        if cached_result:
            return f"Cached result: {cached_result}"

        # Search vector database
        search_results = self.search_vector_db(task, top_k=2)

        # Store intermediate results in memory
        self.store_in_memory(f"search:{task}", search_results)

        # Call external API
        api_response = self.call_external_api(
            "/api/v1/analyze",
            {"query": task, "mode": "deep"}
        )

        # Store final result in cache
        result = f"Processed '{task}' with {len(search_results)} context items"
        self.cache[f"task:{task}"] = result

        return result
