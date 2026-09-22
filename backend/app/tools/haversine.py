import math
from typing import List, Dict, Any
from ..models.route import RouteInfo

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Returns the great-circle distance in kilometers between two lat/lon points using the Haversine formula.
    Mean Earth radius R = 6371.0 km.
    """
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    
    a = math.sin(delta_lat / 2.0) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return round(6371.0 * c, 5)

def find_nearby_stops(
    user_lat: float,
    user_lon: float,
    routes: List[RouteInfo],
    radius_km: float = 2.0
) -> List[Dict[str, Any]]:
    """
    Finds all bus stops within `radius_km` of the user's location.
    Returns results sorted by distance in ascending order.
    """
    nearby_stops = []
    
    for r in routes:
        for s in r.stops:
            dist = haversine_distance(user_lat, user_lon, s.latitude, s.longitude)
            if dist <= radius_km:
                nearby_stops.append({
                    "route_number": r.route_number,
                    "route_name": r.route_name,
                    "bus_type": r.bus_type,
                    "time_slot": r.time_slot,
                    "stop_name": s.name,
                    "timing": s.timing,
                    "latitude": s.latitude,
                    "longitude": s.longitude,
                    "distance_km": round(dist, 3),
                    "driver_name": r.driver_name,
                    "driver_phone": r.driver_phone,
                    "incharge_name": r.incharge_name,
                    "incharge_phone": r.incharge_phone
                })
                
    # Sort strictly by distance ascending
    nearby_stops.sort(key=lambda x: x["distance_km"])
    return nearby_stops
