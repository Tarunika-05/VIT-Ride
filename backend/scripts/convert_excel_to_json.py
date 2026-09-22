import json
import re
import os
import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
EXCEL_UPDATED = BASE_DIR.parent / "Past work" / "routeUpdated.xlsx"
EXCEL_ORIGINAL = BASE_DIR.parent / "Past work" / "routes.xlsx"
OUTPUT_DIR = BASE_DIR / "app" / "data" / "routes"
OUTPUT_FILE = OUTPUT_DIR / "all_routes.json"

DRIVER_NAMES = [
    "Rajesh Kumar", "Suresh Babu", "M. Palani", "K. Murugan", "V. Arumugam",
    "D. Selvan", "G. Mohan", "R. Venkatesh", "T. Saravanan", "S. Mani",
    "P. Senthil", "A. Ravi", "K. Prakash", "N. Chandran", "M. Elumalai",
    "R. Sekar", "J. Jayakumar", "S. Dhanapal", "C. Balaji", "E. Ramesh"
]

INCHARGE_NAMES = [
    "Dr. S. Ramesh", "Prof. K. Venkatesh", "Dr. P. Vijay", "Dr. A. Anand",
    "Dr. R. Karthik", "Dr. N. Saravanan", "Prof. M. Divya", "Dr. K. Sangeetha",
    "Prof. T. Mohan", "Dr. V. Preethi", "Dr. S. Balamurugan", "Prof. R. Priya",
    "Dr. E. Sasikumar", "Dr. G. Sivakumar", "Prof. H. Naveen"
]

def normalize_timing(timing_val) -> str:
    """Normalize timing strings like '6.15 AM', '06.30AM', '13:50:00' to standard 'H:MM AM/PM' format."""
    if pd.isna(timing_val):
        return "7:00 AM"
    
    t_str = str(timing_val).strip()
    
    # Check if format is HH:MM:SS or HH:MM
    match_hms = re.match(r'^(\d{1,2}):(\d{2})(?::(\d{2}))?$', t_str)
    if match_hms:
        hour, minute = int(match_hms.group(1)), int(match_hms.group(2))
        period = "AM" if hour < 12 else "PM"
        hour_12 = hour if 1 <= hour <= 12 else (hour - 12 if hour > 12 else 12)
        return f"{hour_12}:{minute:02d} {period}"
        
    # Replace period with colon: "6.15 AM" -> "6:15 AM"
    t_str = t_str.replace('.', ':')
    
    # Handle missing space before AM/PM: "6:30AM" -> "6:30 AM"
    t_str = re.sub(r'(\d)(AM|PM|am|pm)', r'\1 \2', t_str)
    
    # Capitalize AM/PM
    t_str = t_str.upper()
    
    # If starting with 0 like 06:15 AM -> 6:15 AM
    t_str = re.sub(r'^0(\d:)', r'\1', t_str)
    
    return t_str

def determine_time_slot(route_number: str, timings: list) -> str:
    """Determine whether a route is morning, afternoon, or evening."""
    r_upper = route_number.upper().strip()
    if r_upper.startswith("AF"):
        return "afternoon"
    if r_upper.startswith("EV"):
        return "evening"
        
    # Check timings
    for t in timings:
        if "PM" in t:
            # Check hour
            match = re.match(r'^(\d{1,2}):\d{2}\s*PM', t)
            if match:
                hour = int(match.group(1))
                if hour >= 4 and hour != 12:
                    return "evening"
                elif hour < 4 or hour == 12:
                    return "afternoon"
    return "morning"

def main():
    print(f"Reading primary dataset: {EXCEL_UPDATED}...")
    df_updated = pd.read_excel(EXCEL_UPDATED)
    
    print(f"Reading fallback dataset: {EXCEL_ORIGINAL}...")
    df_orig = pd.read_excel(EXCEL_ORIGINAL)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    routes_dict = {}
    
    # 1. Process updated routes
    for r_no, sub_df in df_updated.groupby('ROUTE_NO', sort=False):
        r_str = str(r_no).strip()
        first_row = sub_df.iloc[0]
        
        stops = []
        for _, row in sub_df.iterrows():
            stops.append({
                "name": str(row['STOP_NAME']).strip(),
                "latitude": round(float(row['LATITUDE']), 6),
                "longitude": round(float(row['LONGITUDE']), 6),
                "timing": normalize_timing(row['TIMING'])
            })
            
        routes_dict[r_str] = {
            "route_number": r_str,
            "route_name": str(first_row.get('ROUTE_NAME', f'Route {r_str}')).strip(),
            "bus_type": str(first_row.get('TYPE', 'NON AC')).strip().upper(),
            "stops": stops
        }
    
    # 2. Add routes from original dataset that are missing in updated (e.g. AF1-AF4, 12, 14, etc.)
    for r_no, sub_df in df_orig.groupby('ROUTE_NO', sort=False):
        r_str = str(r_no).strip()
        if r_str not in routes_dict:
            first_row = sub_df.iloc[0]
            stops = []
            for _, row in sub_df.iterrows():
                stops.append({
                    "name": str(row['STOP_NAME']).strip(),
                    "latitude": round(float(row['LATITUDE']), 6),
                    "longitude": round(float(row['LONGITUDE']), 6),
                    "timing": normalize_timing(row['TIMING'])
                })
            
            # Name heuristic for AF routes or others
            name = f"Route {r_str}"
            if r_str.startswith("AF"):
                name = f"Afternoon Shuttle {r_str}"
            elif len(stops) > 0:
                name = stops[0]["name"]
                
            routes_dict[r_str] = {
                "route_number": r_str,
                "route_name": name,
                "bus_type": "NON AC",
                "stops": stops
            }
            
    # 3. Specifically ensure Route 2 has SHANTHI COLONY (from ICCCNT conference paper Table II)
    # If Route 2 from df_orig has SHANTHI COLONY, let's make sure it's present in Route 2
    if '2' in routes_dict:
        r2_stops = [s["name"].upper() for s in routes_dict['2']['stops']]
        if not any("SHANTHI" in s or "SHANTI" in s for s in r2_stops):
            # Check original df_orig for Route 2 stops
            orig_r2 = df_orig[df_orig['ROUTE_NO'].astype(str) == '2']
            if len(orig_r2) > 0:
                print("Adding conference paper stops (including Shanthi Colony) to Route 2...")
                extra_stops = []
                for _, row in orig_r2.iterrows():
                    s_name = str(row['STOP_NAME']).strip()
                    if s_name.upper() not in r2_stops:
                        extra_stops.append({
                            "name": s_name,
                            "latitude": round(float(row['LATITUDE']), 6),
                            "longitude": round(float(row['LONGITUDE']), 6),
                            "timing": normalize_timing(row['TIMING'])
                        })
                routes_dict['2']['stops'].extend(extra_stops)

    # 4. Finalize contacts and time slots
    routes_list = []
    for i, (r_key, r_data) in enumerate(routes_dict.items()):
        timings = [s["timing"] for s in r_data["stops"]]
        time_slot = determine_time_slot(r_data["route_number"], timings)
        
        driver_name = DRIVER_NAMES[i % len(DRIVER_NAMES)]
        driver_phone = f"+91-98401{10000 + (i * 123) % 89999:05d}"
        
        incharge_name = INCHARGE_NAMES[i % len(INCHARGE_NAMES)]
        incharge_phone = f"+91-94440{20000 + (i * 321) % 79999:05d}"
        
        routes_list.append({
            "route_number": r_data["route_number"],
            "route_name": r_data["route_name"],
            "time_slot": time_slot,
            "bus_type": r_data["bus_type"],
            "driver_name": driver_name,
            "driver_phone": driver_phone,
            "incharge_name": incharge_name,
            "incharge_phone": incharge_phone,
            "stops": r_data["stops"]
        })
        
    output_payload = {"routes": routes_list}
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully compiled {len(routes_list)} total routes into {OUTPUT_FILE}")
    print(f"Morning routes: {sum(1 for r in routes_list if r['time_slot'] == 'morning')}")
    print(f"Afternoon routes: {sum(1 for r in routes_list if r['time_slot'] == 'afternoon')}")
    print(f"Evening routes: {sum(1 for r in routes_list if r['time_slot'] == 'evening')}")
    print(f"Total stops across all routes: {sum(len(r['stops']) for r in routes_list)}")

if __name__ == "__main__":
    main()
