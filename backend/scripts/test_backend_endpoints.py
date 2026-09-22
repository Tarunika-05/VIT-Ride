import os
import sys
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

from fastapi.testclient import TestClient
from backend.app.main import app

def run_tests():
    print("=" * 60)
    print("🚀 TESTING BACKEND API ENDPOINTS")
    print("=" * 60)
    
    with TestClient(app) as client:
        # 1. Health
        r1 = client.get("/health")
        print("\n[1] Health Check:")
        print(f"    Status: {r1.status_code}, Body: {r1.json()}")
        assert r1.status_code == 200
        
        # 2. Routes by time slot
        r2 = client.get("/api/routes?time_slot=morning")
        print(f"\n[2] Morning Routes Query:")
        print(f"    Status: {r2.status_code}, Total Routes: {len(r2.json())}")
        assert r2.status_code == 200
        assert len(r2.json()) > 0
        
        # 3. Specific Route lookup (Route 2)
        r3 = client.get("/api/routes/2")
        print(f"\n[3] Specific Route Lookup (Route 2):")
        data3 = r3.json()
        print(f"    Status: {r3.status_code}, Name: {data3['route_name']}, Bus Type: {data3['bus_type']}")
        print(f"    Driver: {data3['driver_name']} ({data3['driver_phone']})")
        print(f"    Stops count: {len(data3['stops'])}")
        assert r3.status_code == 200
        
        # 4. Nearest stop finder (Haversine using ICCCNT paper coordinates)
        print(f"\n[4] Nearest Stop Finder (Anna Nagar: 13.090476, 80.215826):")
        payload = {"latitude": 13.090476, "longitude": 80.215826, "radius_km": 2.0}
        r4 = client.post("/api/nearest-stop", json=payload)
        data4 = r4.json()
        print(f"    Status: {r4.status_code}, Matches Found: {data4['count']}")
        for s in data4['stops'][:3]:
            print(f"    - Route {s['route_number']} ({s['stop_name']}): {s['distance_km']} km")
        assert r4.status_code == 200
        assert data4['count'] > 0
        
        # 5. AI Chat with Gemini + RAG
        print(f"\n[5] AI Chat Endpoint with RAG:")
        chat_payload = {"message": "Any bus from CMBT in the morning?", "session_id": "test_verification"}
        r5 = client.post("/api/chat", json=chat_payload)
        data5 = r5.json()
        print(f"    Status: {r5.status_code}, Latency: {data5.get('response_time_ms')} ms")
        print(f"    Response snippet:\n    {data5.get('response')[:250]}...\n")
        assert r5.status_code == 200
        assert len(data5.get('response', '')) > 20

    print("=" * 60)
    print("✅ ALL BACKEND ENDPOINT TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
