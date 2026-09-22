import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from ..models.route import RouteInfo, AllRoutes

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "routes" / "all_routes.json"

_cached_routes: Optional[List[RouteInfo]] = None

def load_routes(force_reload: bool = False) -> List[RouteInfo]:
    """
    Load all routes from the JSON data file.
    Caches in memory for fast lookup.
    """
    global _cached_routes
    if _cached_routes is not None and not force_reload:
        return _cached_routes

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Routes data file not found at {DATA_PATH}")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    all_routes = AllRoutes.model_validate(data)
    _cached_routes = all_routes.routes
    return _cached_routes

def get_routes_by_time_slot(routes: List[RouteInfo], slot: str) -> List[RouteInfo]:
    """Filter routes by time_slot (e.g. 'morning', 'afternoon', 'evening')."""
    slot_lower = slot.lower().strip()
    return [r for r in routes if r.time_slot.lower() == slot_lower]

def get_route_by_number(routes: List[RouteInfo], route_num: str) -> Optional[RouteInfo]:
    """Find a route by route_number string (e.g., '1', '1A', '21', 'AF4')."""
    target = str(route_num).strip().upper()
    for r in routes:
        if r.route_number.strip().upper() == target:
            return r
    return None

def get_all_stop_names(routes: List[RouteInfo]) -> List[str]:
    """Return a sorted, unique list of all stop names across all routes."""
    names = set()
    for r in routes:
        for s in r.stops:
            names.add(s.name)
    return sorted(list(names))

def get_unique_route_names(routes: List[RouteInfo]) -> List[Dict[str, str]]:
    """Return unique route numbers and names for UI dropdowns."""
    results = []
    for r in routes:
        results.append({
            "route_number": r.route_number,
            "route_name": r.route_name,
            "bus_type": r.bus_type,
            "time_slot": r.time_slot
        })
    return results

def search_stops_by_area(routes: List[RouteInfo], area_name: str) -> List[Dict[str, Any]]:
    """
    Case-insensitive substring search on stop names across all routes.
    Returns list of stop matches with timing and route metadata.
    """
    query = area_name.strip().lower()
    results = []
    for r in routes:
        for s in r.stops:
            if query in s.name.lower():
                results.append({
                    "route_number": r.route_number,
                    "route_name": r.route_name,
                    "bus_type": r.bus_type,
                    "time_slot": r.time_slot,
                    "stop_name": s.name,
                    "timing": s.timing,
                    "latitude": s.latitude,
                    "longitude": s.longitude,
                    "driver_name": r.driver_name,
                    "driver_phone": r.driver_phone
                })
    return results
