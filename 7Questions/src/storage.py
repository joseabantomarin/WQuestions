"""7D coordinate storage — sparse tensor via dict."""

from typing import Any, Optional, Dict, Tuple


class StorageCoords:
    """Sparse 7D storage: (q, o, l, t, n, k, m) → value."""

    def __init__(self):
        self.data: Dict[Tuple, Any] = {}

    def put(self, q, o, l, t, n, k, m, value: Any) -> None:
        """Store value at coordinate."""
        key = (q, o, l, t, n, k, m)
        self.data[key] = value

    def get(self, q, o, l, t, n, k, m) -> Optional[Any]:
        """Retrieve value at coordinate."""
        key = (q, o, l, t, n, k, m)
        return self.data.get(key)

    def query(self, q=None, o=None, l=None, t=None, n=None, k=None, m=None) -> list:
        """
        Slice the tensor: return all points matching the filter.
        None = wildcard.

        Returns: [(q,o,l,t,n,k,m,value), ...]
        """
        results = []
        for (dq, do, dl, dt, dn, dk, dm), value in self.data.items():
            if (q is None or dq == q) and \
               (o is None or do == o) and \
               (l is None or dl == l) and \
               (t is None or dt == t) and \
               (n is None or dn == n) and \
               (k is None or dk == k) and \
               (m is None or dm == m):
                results.append((dq, do, dl, dt, dn, dk, dm, value))
        return results

    def show_state(self) -> dict:
        """Export entire state as dict."""
        return {
            "points": len(self.data),
            "data": {str(k): v for k, v in self.data.items()}
        }

    def delete(self, q, o, l, t, n, k, m) -> bool:
        """Delete point, return True if existed."""
        key = (q, o, l, t, n, k, m)
        if key in self.data:
            del self.data[key]
            return True
        return False
