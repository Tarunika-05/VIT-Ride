from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Optional, Dict, Any
from ..models.route import RouteInfo, NearestStopRequest
from ..services.route_service import (
    load_routes,
    get_routes_by_time_slot,
    get_route_by_number,
    get_all_stop_names,
    get_unique_route_names
)
from ..tools.haversine import find_nearby_stops

router = APIRouter(tags=["Routes"])

@router.get("/routes", response_model=List[RouteInfo])
async def list_routes(
    time_slot: Optional[str] = Query(None, description="Filter by time slot: morning, afternoon, evening"),
    request: Request = None
):
    """
    List routes, optionally filtered by time slot.
    Replicates the conference paper's time-slot route filtering.
    """
    routes = getattr(request.app.state, "routes", None) or load_routes()
    if time_slot:
        return get_routes_by_time_slot(routes, time_slot)
    return routes

@router.get("/routes/{route_number}", response_model=RouteInfo)
async def get_route(route_number: str, request: Request = None):
    """
    Get detailed stop sequences and driver contacts for a specific route number.
    """
    routes = getattr(request.app.state, "routes", None) or load_routes()
    route = get_route_by_number(routes, route_number)
    if not route:
        raise HTTPException(status_code=404, detail=f"Route '{route_number}' not found.")
    return route

@router.post("/nearest-stop")
async def find_nearest(payload: NearestStopRequest, request: Request = None):
    """
    Find nearest stops within given radius using Haversine formula.
    Matches the conference paper Table II implementation.
    """
    routes = getattr(request.app.state, "routes", None) or load_routes()
    nearby = find_nearby_stops(
        user_lat=payload.latitude,
        user_lon=payload.longitude,
        routes=routes,
        radius_km=payload.radius_km
    )
    return {
        "status": "Stops Found" if nearby else "No Stops Found",
        "count": len(nearby),
        "radius_km": payload.radius_km,
        "user_coordinates": {"latitude": payload.latitude, "longitude": payload.longitude},
        "stops": nearby
    }

@router.get("/route-names")
async def list_route_names(request: Request = None):
    """
    Returns unique route numbers and names for frontend dropdown population.
    """
    routes = getattr(request.app.state, "routes", None) or load_routes()
    return {"routes": get_unique_route_names(routes)}

@router.get("/stops")
async def list_all_stops(request: Request = None):
    """
    Returns sorted list of all unique stop names across all routes.
    """
    routes = getattr(request.app.state, "routes", None) or load_routes()
    return {"stops": get_all_stop_names(routes)}
