from typing import List, Dict, Any
from ..models.route import RouteInfo

def generate_route_documents(routes: List[RouteInfo]) -> List[Dict[str, Any]]:
    """
    Converts structured RouteInfo objects into rich text documents with metadata
    for vector database indexing and semantic retrieval.
    """
    documents = []
    
    for r in routes:
        stops_text = []
        stop_names_list = []
        for idx, s in enumerate(r.stops, start=1):
            stops_text.append(f"  {idx}. {s.name} at {s.timing} (lat: {s.latitude}, lon: {s.longitude})")
            stop_names_list.append(s.name)
            
        stops_formatted = "\n".join(stops_text) if stops_text else "  No specific intermediate stops listed."
        areas_served = ", ".join(stop_names_list)
        
        doc_text = f"""Route Number: Route {r.route_number}
Route Name: {r.route_name}
Bus Category: {r.bus_type}
Time Slot: {r.time_slot.capitalize()}
Driver: {r.driver_name} (Phone: {r.driver_phone})
Faculty In-Charge: {r.incharge_name} (Phone: {r.incharge_phone})
Total Stops: {len(r.stops)}
Areas and Stops Served: {areas_served}
Scheduled Stops and Departure Times:
{stops_formatted}
Final Destination: VIT Chennai Campus, Vandalur-Kelambakkam Road.
"""
        
        metadata = {
            "route_number": r.route_number,
            "route_name": r.route_name,
            "bus_type": r.bus_type,
            "time_slot": r.time_slot,
            "driver_name": r.driver_name,
            "driver_phone": r.driver_phone,
            "incharge_name": r.incharge_name,
            "incharge_phone": r.incharge_phone,
            "stop_count": len(r.stops)
        }
        
        doc_id = f"route_{r.route_number}_{r.time_slot}".lower().replace(" ", "_")
        
        documents.append({
            "id": doc_id,
            "text": doc_text.strip(),
            "metadata": metadata
        })
        
    return documents
