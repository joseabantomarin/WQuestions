"""Benchmark: coordinates vs triplets."""

import sys
sys.path.insert(0, '/Users/joseabanto/WQuestions/7Questions')

import json
import time
from src.api import SevenQuestionsAPI


# Triplet representation (traditional)
class TripletStore:
    def __init__(self):
        self.data = []

    def assert_fact(self, subject, role, value):
        self.data.append({
            "subject": subject,
            "role": role,
            "value": value
        })

    def serialize(self):
        return json.dumps(self.data)


def benchmark_serialization():
    """Compare size of serialized data."""
    print("\n📊 SERIALIZATION SIZE")
    print("=" * 50)

    # Setup: a typical sale with multiple facts
    coords_api = SevenQuestionsAPI()
    triplet_store = TripletStore()

    # Same data in both formats
    facts = [
        ("juan", "venta_1", None, None, 50, "libro", "vendedor", "juan"),
        ("maria", "venta_1", None, None, 50, "libro", "comprador", "maria"),
        ("venta_1", None, None, None, None, "libro", "item", "venta_1"),
        (None, "venta_1", None, None, 50, None, "monto", 50),
        (None, "venta_1", None, None, None, None, "moneda", "USD"),
    ]

    # Add to both stores
    for q, o, l, t, n, k, m, value in facts:
        coords_api.assert_fact(q, o, l, t, n, k, m, value)
        triplet_store.assert_fact(f"{q or 'venta_1'}", f"{m or 'unknown'}", value)

    # Serialize
    coords_json = coords_api.serialize_for_llm()
    triplet_json = triplet_store.serialize()

    coords_size = len(coords_json)
    triplet_size = len(triplet_json)
    saving = 100 * (1 - coords_size / triplet_size)

    print(f"Coordinates: {coords_size} bytes")
    print(f"Triplets:    {triplet_size} bytes")
    print(f"Saving:      {saving:.1f}%")
    print()
    print("Coords JSON (compact):")
    print(coords_json[:200] + "..." if len(coords_json) > 200 else coords_json)
    print()
    print("Triplets JSON (verbose):")
    print(triplet_json[:200] + "..." if len(triplet_json) > 200 else triplet_json)


def benchmark_operations():
    """Compare operation speed."""
    print("\n⚡ OPERATION SPEED")
    print("=" * 50)

    api = SevenQuestionsAPI()
    n = 1000

    # Benchmark put
    start = time.time()
    for i in range(n):
        api.assert_fact(f"entity_{i}", f"prop_{i % 10}", None, None, i, None, None, f"value_{i}")
    put_time = time.time() - start

    # Benchmark query
    start = time.time()
    for i in range(n):
        api.ask(o=f"prop_{i % 10}")
    query_time = time.time() - start

    # Benchmark show_model
    start = time.time()
    for i in range(10):
        api.show_model()
    show_time = time.time() - start

    print(f"Put {n} points:  {put_time*1000:.2f} ms ({put_time/n*1e6:.2f} µs/op)")
    print(f"Query {n} times: {query_time*1000:.2f} ms ({query_time/n*1e6:.2f} µs/op)")
    print(f"Show model 10x:  {show_time*1000:.2f} ms ({show_time/10*1000:.2f} ms/op)")


def benchmark_llm_tokens():
    """Estimate token usage (rough heuristic)."""
    print("\n🔤 TOKEN ESTIMATION")
    print("=" * 50)

    # Rough: ~4 chars per token for typical JSON
    coords_json = '[[q,o,l,t,n,k,m,val], ...]'
    triplet_json = '[{"subject":"...", "role":"...", "value":"..."}, ...]'

    # Create realistic data
    coords_api = SevenQuestionsAPI()
    for i in range(100):
        coords_api.assert_fact(f"e_{i}", None, None, None, i, None, None, f"v_{i}")

    coords_data = coords_api.serialize_for_llm()
    coords_tokens = len(coords_data) / 4

    # Triplet equivalent (rough)
    triplet_data = json.dumps([
        {"subject": f"e_{i}", "role": "value", "value": f"v_{i}"}
        for i in range(100)
    ])
    triplet_tokens = len(triplet_data) / 4

    saving = 100 * (1 - coords_tokens / triplet_tokens)
    print(f"Coords 100 points:  ~{coords_tokens:.0f} tokens")
    print(f"Triplets 100 points: ~{triplet_tokens:.0f} tokens")
    print(f"Saving: {saving:.1f}%")


if __name__ == "__main__":
    print("\n🧪 7Questions Benchmark Suite")
    print("Comparing: Coordinate Storage vs Traditional Triplets")

    benchmark_serialization()
    benchmark_operations()
    benchmark_llm_tokens()

    print("\n✅ Benchmark complete")
