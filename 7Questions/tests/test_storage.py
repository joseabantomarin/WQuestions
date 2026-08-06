"""Tests for 7D storage."""

import sys
sys.path.insert(0, '/Users/joseabanto/WQuestions/7Questions/src')

from storage import StorageCoords


def test_put_and_get():
    """Test basic put/get."""
    store = StorageCoords()
    store.put("juan", "venta_123", None, None, 50, "libro", "vendedor", "activo")

    result = store.get("juan", "venta_123", None, None, 50, "libro", "vendedor")
    assert result == "activo"


def test_query_wildcard():
    """Test query with None wildcards."""
    store = StorageCoords()
    store.put("juan", "venta_1", None, None, 50, "libro", "vendedor", True)
    store.put("maria", "venta_1", None, None, 50, "libro", "comprador", True)
    store.put("juan", "venta_2", None, None, 30, "pen", "vendedor", True)

    # All ventas
    results = store.query(o="venta_1")
    assert len(results) == 2

    # Solo juan
    results = store.query(q="juan")
    assert len(results) == 2

    # juan + venta_1
    results = store.query(q="juan", o="venta_1")
    assert len(results) == 1


def test_delete():
    """Test deletion."""
    store = StorageCoords()
    store.put("juan", "venta_1", None, None, 50, "libro", "vendedor", True)

    assert store.delete("juan", "venta_1", None, None, 50, "libro", "vendedor") == True
    assert store.get("juan", "venta_1", None, None, 50, "libro", "vendedor") is None
    assert store.delete("juan", "venta_1", None, None, 50, "libro", "vendedor") == False


if __name__ == "__main__":
    test_put_and_get()
    test_query_wildcard()
    test_delete()
    print("✓ All storage tests passed")
