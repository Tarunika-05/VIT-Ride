import os
import sys
import time
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.app.services.route_service import load_routes
from backend.app.services.vector_store import RouteVectorStore

# Benchmark queries with ground-truth expected route numbers
EVAL_QUERIES = [
    {"query": "Any morning bus from CMBT?", "expected_routes": ["2", "21"]},
    {"query": "Bus stops near Thirumangalam", "expected_routes": ["1A", "3"]},
    {"query": "Route serving Padi Saravana Stores", "expected_routes": ["1"]},
    {"query": "Who is the driver for Route 2?", "expected_routes": ["2"]},
    {"query": "Buses through Velachery Vijayanagar", "expected_routes": ["15B", "18B", "AF4"]},
    {"query": "Afternoon shuttle bus to Mambakkam", "expected_routes": ["AF4"]},
    {"query": "Bus near Shanthi Colony Anna Nagar", "expected_routes": ["2", "23"]},
    {"query": "Buses departing from Vadapalani", "expected_routes": ["2", "21"]},
    {"query": "Routes through Tambaram station", "expected_routes": ["21", "51"]},
    {"query": "AC bus options in the morning", "expected_routes": ["1", "1A", "2"]},
    {"query": "Morning bus serving Pallavaram", "expected_routes": ["21", "50"]},
    {"query": "Bus route near Porur Junction", "expected_routes": ["8", "1A"]},
    {"query": "Routes serving Medavakkam", "expected_routes": ["18B", "AF4"]},
    {"query": "Buses through Guindy or Alandur Metro", "expected_routes": ["21"]},
    {"query": "Route serving Thiruvanmiyur", "expected_routes": ["46"]}
]

def run_eval():
    print("=" * 70)
    print("🔍 RAG RETRIEVAL ACCURACY & LATENCY BENCHMARK")
    print("=" * 70)

    routes = load_routes()
    vector_store = RouteVectorStore()
    vector_store.index_routes(routes)

    total_queries = len(EVAL_QUERIES)
    p_at_1_hits = 0
    p_at_3_hits = 0
    p_at_5_hits = 0
    latencies = []

    print(f"{'Query':<38} | {'Retrieved Top 3':<20} | {'Hit@3':<6} | {'Latency':<8}")
    print("-" * 78)

    for item in EVAL_QUERIES:
        query = item["query"]
        expected = item["expected_routes"]

        start = time.time()
        results = vector_store.search(query, n_results=5)
        elapsed_ms = round((time.time() - start) * 1000.0, 2)
        latencies.append(elapsed_ms)

        retrieved_routes = [r["metadata"].get("route_number") for r in results]

        # Precision checks
        hit_1 = any(r in expected for r in retrieved_routes[:1])
        hit_3 = any(r in expected for r in retrieved_routes[:3])
        hit_5 = any(r in expected for r in retrieved_routes[:5])

        if hit_1: p_at_1_hits += 1
        if hit_3: p_at_3_hits += 1
        if hit_5: p_at_5_hits += 1

        top3_str = ", ".join(retrieved_routes[:3])
        status = "PASS" if hit_3 else "FAIL"
        print(f"{query[:38]:<38} | {top3_str[:20]:<20} | {status:<6} | {elapsed_ms} ms")

    p1_score = round((p_at_1_hits / total_queries) * 100.0, 1)
    p3_score = round((p_at_3_hits / total_queries) * 100.0, 1)
    p5_score = round((p_at_5_hits / total_queries) * 100.0, 1)
    avg_latency = round(sum(latencies) / len(latencies), 2)

    print("=" * 78)
    print("📊 BENCHMARK SUMMARY METRICS:")
    print(f"  • Precision@1: {p1_score}% ({p_at_1_hits}/{total_queries})")
    print(f"  • Precision@3: {p3_score}% ({p_at_3_hits}/{total_queries})")
    print(f"  • Precision@5: {p5_score}% ({p_at_5_hits}/{total_queries})")
    print(f"  • Mean Retrieval Latency: {avg_latency} ms")
    print("=" * 78)

if __name__ == "__main__":
    run_eval()
