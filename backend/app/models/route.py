from pydantic import BaseModel, Field
from typing import List, Optional

class Stop(BaseModel):
    name: str = Field(..., description="Name of the boarding point or stop")
    latitude: float = Field(..., description="Latitude of the stop")
    longitude: float = Field(..., description="Longitude of the stop")
    timing: str = Field(..., description="Scheduled departure timing, e.g. '6:15 AM'")

class RouteInfo(BaseModel):
    route_number: str = Field(..., description="Route identifier, e.g. '1', '1A', 'AF4'")
    route_name: str = Field(..., description="General route designation, e.g. 'PADI SARAVANA'")
    time_slot: str = Field(default="morning", description="Time slot: morning, afternoon, evening")
    bus_type: str = Field(default="NON AC", description="Bus category: AC or NON AC")
    driver_name: str = Field(..., description="Driver contact name")
    driver_phone: str = Field(..., description="Driver phone number")
    incharge_name: str = Field(..., description="Faculty or staff route in-charge name")
    incharge_phone: str = Field(..., description="In-charge phone number")
    stops: List[Stop] = Field(default_factory=list, description="Ordered list of stops on this route")

class AllRoutes(BaseModel):
    routes: List[RouteInfo]

class NearestStopRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 2.0

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    response_time_ms: Optional[float] = None
