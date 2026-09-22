import os
import requests
from typing import Dict, Any, Optional
from ..config import settings
from .haversine import haversine_distance

ROUTES_API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

def get_travel_time(
    origin_lat: float, origin_lon: float,
    dest_lat: float, dest_lon: float,
    mode: str = "walking",  # "walking" or "driving"
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes travel time and distance between origin and destination.
    Uses Google Routes API v2, with a mathematical fallback if API is unavailable.
    """
    key = api_key or settings.GOOGLE_MAPS_API_KEY
    travel_mode = "WALK" if mode.lower() == "walking" else "DRIVE"
    
    if key:
        try:
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": key,
                "X-Goog-FieldMask": "routes.duration,routes.distanceMeters"
            }
            payload = {
                "origin": {"location": {"latLng": {"latitude": origin_lat, "longitude": origin_lon}}},
                "destination": {"location": {"latLng": {"latitude": dest_lat, "longitude": dest_lon}}},
                "travelMode": travel_mode
            }
            res = requests.post(ROUTES_API_URL, headers=headers, json=payload, timeout=8)
            if res.status_code == 200:
                data = res.json()
                routes = data.get("routes", [])
                if routes:
                    dist_meters = routes[0].get("distanceMeters", 0)
                    dur_str = routes[0].get("duration", "0s").replace("s", "")
                    dur_seconds = float(dur_str) if dur_str else 0
                    
                    dist_km = round(dist_meters / 1000.0, 2)
                    dur_min = round(dur_seconds / 60.0, 1)
                    return {
                        "distance_km": dist_km,
                        "duration_minutes": dur_min,
                        "distance_text": f"{dist_km} km",
                        "duration_text": f"{int(dur_min)} mins",
                        "mode": mode,
                        "source": "google_routes_api"
                    }
        except Exception as e:
            # Fallback will take over
            pass

    # Fallback estimation based on Haversine distance with road circuity factor
    straight_dist = haversine_distance(origin_lat, origin_lon, dest_lat, dest_lon)
    road_dist = straight_dist * 1.35  # standard urban circuity factor
    
    if mode.lower() == "walking":
        speed_kmh = 4.8  # average walking speed
    else:
        speed_kmh = 22.0  # average city bus speed in Chennai traffic
        
    est_duration_min = max(1.0, round((road_dist / speed_kmh) * 60.0, 1))
    dist_km = round(road_dist, 2)
    
    return {
        "distance_km": dist_km,
        "duration_minutes": est_duration_min,
        "distance_text": f"{dist_km} km (est.)",
        "duration_text": f"{int(est_duration_min)} mins (est.)",
        "mode": mode,
        "source": "urban_transit_heuristic"
    }

def compute_trip_plan(
    user_lat: float, user_lon: float,
    stop_lat: float, stop_lon: float,
    stop_departure_time: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes total journey plan:
    1. Walk from user's current location to candidate stop.
    2. Bus travel from stop to VIT Chennai Campus.
    3. Total trip duration (walk time + bus travel time).
    """
    walk_info = get_travel_time(
        user_lat, user_lon,
        stop_lat, stop_lon,
        mode="walking",
        api_key=api_key
    )
    
    bus_info = get_travel_time(
        stop_lat, stop_lon,
        settings.VIT_CAMPUS_LAT, settings.VIT_CAMPUS_LON,
        mode="driving",
        api_key=api_key
    )
    
    total_minutes = round(walk_info["duration_minutes"] + bus_info["duration_minutes"], 1)
    
    return {
        "walk_to_stop": walk_info,
        "bus_to_campus": bus_info,
        "stop_departure_time": stop_departure_time,
        "total_trip_minutes": total_minutes,
        "total_trip_text": f"{int(total_minutes)} mins"
    }
