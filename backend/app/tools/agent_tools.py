from typing import Optional, List, Dict, Any
from ..config import settings
from ..services.route_service import load_routes, get_route_by_number, search_stops_by_area
from .haversine import find_nearby_stops, haversine_distance
from .directions import get_travel_time, compute_trip_plan

def find_nearby_stops_tool(user_lat: float, user_lon: float, radius_km: float = 2.0) -> str:
    """
    Finds bus stops within a given radius of user coordinates using the Haversine formula.
    Returns a human-readable list of matching stops with routes and distances.
    """
    routes = load_routes()
    nearby = find_nearby_stops(user_lat, user_lon, routes, radius_km=radius_km)
    
    if not nearby:
        return f"No VIT bus stops found within {radius_km} km of coordinates ({user_lat:.4f}, {user_lon:.4f}). Try increasing the search radius."
        
    lines = [f"Found {len(nearby)} stop(s) within {radius_km} km of your location:"]
    for s in nearby[:8]:
        lines.append(
            f"- Route {s['route_number']} ({s['route_name']}): **{s['stop_name']}** "
            f"at **{s['timing']}** — {s['distance_km']} km away ({s['bus_type']})"
        )
    return "\n".join(lines)

def get_travel_time_tool(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float, mode: str = "walking") -> str:
    """
    Computes real transit or walking travel duration and distance between two locations.
    """
    res = get_travel_time(origin_lat, origin_lon, dest_lat, dest_lon, mode=mode)
    return f"Estimated {mode} trip: {res['distance_text']}, taking approximately {res['duration_text']}."

def search_routes_tool(query: str, vector_store=None) -> str:
    """
    Searches the bus route database for stops, areas, schedules, or driver contacts.
    """
    routes = load_routes()
    # 1. First check area substring
    area_matches = search_stops_by_area(routes, query)
    if area_matches:
        lines = [f"Found {len(area_matches)} route(s) serving '{query}':"]
        for m in area_matches[:6]:
            lines.append(
                f"- Route {m['route_number']} ({m['route_name']}): **{m['stop_name']}** "
                f"departs at **{m['timing']}** ({m['bus_type']}). Driver: {m['driver_name']} ({m['driver_phone']})"
            )
        return "\n".join(lines)
        
    # 2. Check semantic vector store if provided
    if vector_store:
        results = vector_store.search(query, n_results=3)
        if results:
            lines = [f"Relevant bus routes found for '{query}':"]
            for r in results:
                meta = r['metadata']
                lines.append(f"- Route {meta.get('route_number')} ({meta.get('route_name')}): {meta.get('bus_type')} - Served areas: {r['text'][:120]}...")
            return "\n".join(lines)
            
    return f"No bus routes or stops found matching '{query}'. Please check the area spelling."

def get_route_details_tool(route_number: str) -> str:
    """
    Retrieves full details of a specific route including stops, timings, driver, and in-charge.
    """
    routes = load_routes()
    r = get_route_by_number(routes, route_number)
    if not r:
        return f"Route '{route_number}' not found in the VIT Chennai transit system."
        
    stops_fmt = "\n".join([f"  {i}. {s.name} — {s.timing}" for i, s in enumerate(r.stops, start=1)])
    return f"""**Route {r.route_number}: {r.route_name}** ({r.bus_type})
- Time Slot: {r.time_slot.capitalize()}
- Driver: {r.driver_name} ({r.driver_phone})
- Route In-Charge: {r.incharge_name} ({r.incharge_phone})
- Stops & Timings:
{stops_fmt}
- Destination: VIT Chennai Campus"""

def plan_trip_tool(user_lat: float, user_lon: float, target_arrival_time: str = "") -> str:
    """
    Multi-step goal-directed trip planner:
    1. Finds nearby stops within 3 km using Haversine.
    2. Computes walking time to each stop + bus duration to campus.
    3. Identifies the fastest overall trip (walk + bus travel).
    4. Explains trade-offs between walking distance and total transit duration.
    """
    routes = load_routes()
    nearby = find_nearby_stops(user_lat, user_lon, routes, radius_km=3.5)
    
    if not nearby:
        return f"No bus stops found within 3.5 km of ({user_lat:.4f}, {user_lon:.4f}) to plan a trip to campus."
        
    plans = []
    # Evaluate top 4 candidate stops
    for s in nearby[:4]:
        trip = compute_trip_plan(
            user_lat, user_lon,
            s["latitude"], s["longitude"],
            s["timing"]
        )
        plans.append({
            "stop": s,
            "walk_min": trip["walk_to_stop"]["duration_minutes"],
            "walk_dist": trip["walk_to_stop"]["distance_text"],
            "bus_min": trip["bus_to_campus"]["duration_minutes"],
            "bus_dist": trip["bus_to_campus"]["distance_text"],
            "total_min": trip["total_trip_minutes"],
            "departure": s["timing"]
        })
        
    # Sort by total trip time
    plans.sort(key=lambda x: x["total_min"])
    best = plans[0]
    
    output = [
        f"🎯 **Trip Recommendation to VIT Chennai Campus:**\n",
        f"**Best Recommended Route**: **Route {best['stop']['route_number']}** from **{best['stop']['stop_name']}**",
        f"- **Bus Departure Time**: {best['departure']}",
        f"- **Walk to Stop**: {best['walk_dist']} (~{int(best['walk_min'])} mins)",
        f"- **Bus Ride to Campus**: {best['bus_dist']} (~{int(best['bus_min'])} mins)",
        f"- **Total Journey Duration**: **{int(best['total_min'])} minutes**\n"
    ]
    
    if len(plans) > 1:
        output.append("📋 **Alternative Options Compared:**")
        for p in plans[1:]:
            diff = int(p['total_min'] - best['total_min'])
            output.append(
                f"- Route {p['stop']['route_number']} from {p['stop']['stop_name']} "
                f"({p['departure']}): Total {int(p['total_min'])} mins (+{diff} mins, walk: {p['walk_dist']})"
            )
            
    if target_arrival_time:
        output.append(f"\n*Target arrival: {target_arrival_time}*")
        
    return "\n".join(output)
