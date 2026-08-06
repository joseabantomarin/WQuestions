"""High-level API for 7D storage."""

from .storage import StorageCoords
import json
from typing import Any, Optional


class SevenQuestionsAPI:
    """User-facing API for 7D coordinate storage."""

    def __init__(self):
        self.store = StorageCoords()

    def assert_fact(self, q, o, l, t, n, k, m, value: Any) -> dict:
        """
        Store a fact as a 7D point.

        Returns: {status: "ok", coordinate: [...]}
        """
        self.store.put(q, o, l, t, n, k, m, value)
        return {
            "status": "ok",
            "coordinate": [q, o, l, t, n, k, m, value]
        }

    def ask(self, q=None, o=None, l=None, t=None, n=None, k=None, m=None) -> dict:
        """
        Query points matching filters (None = wildcard).

        Returns: {found: N, results: [(q,o,l,t,n,k,m,value), ...]}
        """
        results = self.store.query(q, o, l, t, n, k, m)
        return {
            "found": len(results),
            "results": results
        }

    def erase(self, q, o, l, t, n, k, m) -> dict:
        """Delete a point."""
        existed = self.store.delete(q, o, l, t, n, k, m)
        return {
            "status": "ok" if existed else "not_found",
            "deleted": existed
        }

    def show_model(self) -> dict:
        """Export entire state."""
        return self.store.show_state()

    def reset(self) -> dict:
        """Clear all data."""
        self.store.data.clear()
        return {"status": "ok", "cleared": True}

    def serialize_for_llm(self) -> str:
        """
        Serialize state as JSON for LLM consumption.
        Compact format: [[q,o,l,t,n,k,m,value], ...]
        """
        points = []
        for (q, o, l, t, n, k, m), value in self.store.data.items():
            points.append([q, o, l, t, n, k, m, value])
        return json.dumps(points, default=str)
