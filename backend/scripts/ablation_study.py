import os
import sys
import csv
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
from backend.app.tools.haversine import find_nearby_stops
from backend.app.tools.directions import compute_trip_plan

# 20 Commuter test locations across Chennai Metropolitan Area
TEST_LOCATIONS = [
    {"name": "Anna Nagar (Shanthi Colony)", "lat": 13.090476, "lon": 80.215826},
    {"name": "Chromepet Station", "lat": 12.951600, "lon": 80.146200},
    {"name": "Vadapalani Junction", "lat": 13.050000, "lon": 80.212000},
    {"name": "Tambaram Sanatorium", "lat": 12.930000, "lon": 80.120000},
    {"name": "Guindy Metro", "lat": 13.006700, "lon": 80.202500},
    {"name": "Velachery Vijayanagar", "lat": 12.975000, "lon": 80.221000},
    {"name": "Porur Roundtana", "lat": 13.038000, "lon": 80.156000},
    {"name": "Medavakkam Koot Road", "lat": 12.916500, "lon": 80.192000},
    {"name": "Pallavaram Bus Stand", "lat": 12.967500, "lon": 80.149100},
    {"name": "Perungalathur Junction", "lat": 12.905000, "lon": 80.089000},
    {"name": "Thiruvanmiyur Bus Depot", "lat": 12.983000, "lon": 80.259400},
    {"name": "CMBT Koyambedu", "lat": 13.067400, "lon": 80.205500},
    {"name": "Camp Road Selaiyur", "lat": 12.906800, "lon": 80.142600},
    {"name": "Kelambakkam Junction", "lat": 12.788000, "lon": 80.219000},
    {"name": "Madipakkam", "lat": 12.963000, "lon": 80.198000},
    {"name": "Adyar Signal", "lat": 13.001200, "lon": 80.256500},
    {"name": "T. Nagar Panagal Park", "lat": 13.040500, "lon": 80.233700},
    {"name": "KK Nagar Depot", "lat": 13.041000, "lon": 80.198000},
    {"name": "Saidapet Subway", "lat": 13.020000, "lon": 80.223000},
    {"name": "Moolakadai Junction", "lat": 13.125000, "lon": 80.235000}
]

def run_ablation():
    print("=" * 70)
    print("📊 RUNNING EMPIRICAL ABLATION STUDY (Journal Extension)")
    print("   Comparing C1 (Haversine-Only) vs C3 (Intelligent Trip Planner)")
    print("=" * 70)

    routes = load_routes()
    results = []
    output_csv = BACKEND_DIR / "scripts" / "ablation_results.csv"

    for loc in TEST_LOCATIONS:
        lat, lon, name = loc["lat"], loc["lon"], loc["name"]
        
        # --- C1: Haversine Only (Conference baseline) ---
        nearby = find_nearby_stops(lat, lon, routes, radius_km=4.0)
        if not nearby:
            continue
            
        c1_stop = nearby[0]
        c1_trip = compute_trip_plan(lat, lon, c1_stop["latitude"], c1_stop["longitude"], c1_stop["timing"])
        c1_total_min = c1_trip["total_trip_minutes"]
        
        # --- C3: Full Agent Optimization across candidates ---
        candidate_evals = []
        for cand in nearby[:5]:
            trip = compute_trip_plan(lat, lon, cand["latitude"], cand["longitude"], cand["timing"])
            candidate_evals.append({
                "stop": cand,
                "total_min": trip["total_trip_minutes"]
            })
            
        candidate_evals.sort(key=lambda x: x["total_min"])
        best_c3 = candidate_evals[0]
        c3_stop = best_c3["stop"]
        c3_total_min = best_c3["total_min"]
        
        minutes_saved = round(c1_total_min - c3_total_min, 1)
        suboptimal = (c1_stop["stop_name"] != c3_stop["stop_name"]) and (minutes_saved > 0)
        
        results.append({
            "Location": name,
            "C1_Stop": f"{c1_stop['stop_name']} (R-{c1_stop['route_number']})",
            "C1_Dist_km": c1_stop["distance_km"],
            "C1_Total_Mins": c1_total_min,
            "C3_Stop": f"{c3_stop['stop_name']} (R-{c3_stop['route_number']})",
            "C3_Total_Mins": c3_total_min,
            "Minutes_Saved": minutes_saved,
            "Haversine_Suboptimal": "YES" if suboptimal else "NO"
        })

    # Save to CSV
    keys = results[0].keys()
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nCompleted study across {len(results)} locations.")
    suboptimal_count = sum(1 for r in results if r["Haversine_Suboptimal"] == "YES")
    suboptimal_pct = round((suboptimal_count / len(results)) * 100.0, 1)
    avg_saved = round(sum(r["Minutes_Saved"] for r in results) / len(results), 1)

    print(f"\n📈 Key Empirical Findings:")
    print(f"  - Haversine picked suboptimal route in: {suboptimal_count}/{len(results)} locations ({suboptimal_pct}%)")
    print(f"  - Average travel time saved by AI Agent: {avg_saved} minutes per commuter trip")
    print(f"  - Results saved to: {output_csv}\n")

    # Display sample preview
    print(f"{'Location':<24} | {'C1 Stop (Nearest)':<25} | {'C3 Stop (Fastest)':<25} | {'Saved (mins)':<12}")
    print("-" * 92)
    for r in results[:6]:
        print(f"{r['Location'][:24]:<24} | {r['C1_Stop'][:25]:<25} | {r['C3_Stop'][:25]:<25} | {r['Minutes_Saved']:<12}")
    print("=" * 92)

if __name__ == "__main__":
    run_ablation()
