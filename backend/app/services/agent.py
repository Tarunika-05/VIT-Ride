import re
from typing import Optional, List, Dict
import google.generativeai as genai
from ..config import settings
from .vector_store import RouteVectorStore
from .memory import memory_manager
from .rag_service import rag_query
from ..tools.agent_tools import (
    find_nearby_stops_tool,
    get_route_details_tool,
    search_routes_tool,
    plan_trip_tool
)

AGENT_SYSTEM_INSTRUCTION = """You are the intelligent VIT Chennai Campus Transit Assistant.
You help commuters navigate the bus system, find routes, compare travel options, and reach campus on time.

You have access to verified real-world tools:
1. Route Search: finding buses serving any Chennai neighborhood or boarding point.
2. Trip Planning: finding the fastest route (walk + bus) using real transit speeds and distances.
3. Route Details: retrieving exact stop lists, driver contacts, and faculty in-charge numbers.
4. Haversine Nearest Stops: finding bus stops near given GPS coordinates.

Behavior Rules:
- If the user provides latitude and longitude, use the coordinates to recommend the best stop and total journey time.
- If the user asks about an area (e.g. CMBT, Vadapalani, Tambaram, Anna Nagar), detail the route numbers and morning/afternoon schedules.
- If the user asks a follow-up question (e.g., 'What if I leave 20 minutes later?' or 'What about afternoon buses?'), use the previous conversation context to re-evaluate and give an updated recommendation.
- Always provide clear, well-structured Markdown answers.
"""

class TransitAgent:
    def __init__(self, vector_store: RouteVectorStore):
        self.vector_store = vector_store
        self.memory = memory_manager
        
    async def chat(self, message: str, session_id: str = "default") -> str:
        """
        Process a user message through the intelligent transit assistant.
        Maintains conversational state per session_id.
        """
        user_text = message.strip()
        history = self.memory.get_history(session_id)
        
        # 1. Check for coordinates in message: e.g. "13.0904, 80.2158" or "lat 13.09, lon 80.21"
        coords_match = re.search(r'([0-9]{1,2}\.[0-9]{3,7})\s*,\s*([0-9]{1,2}\.[0-9]{3,7})', user_text)
        if coords_match:
            lat, lon = float(coords_match.group(1)), float(coords_match.group(2))
            response_text = plan_trip_tool(lat, lon)
            self.memory.add_message(session_id, "user", user_text)
            self.memory.add_message(session_id, "assistant", response_text)
            return response_text

        # 2. Check for route number query: e.g. "Route 12", "tell me about route 1A"
        route_match = re.search(r'\broute\s+([0-9]{1,2}[a-zA-Z]?|af[1-4])\b', user_text.lower())
        if route_match and any(w in user_text.lower() for w in ["who drives", "details", "contact", "stops", "driver", "incharge"]):
            r_no = route_match.group(1).upper()
            response_text = get_route_details_tool(r_no)
            self.memory.add_message(session_id, "user", user_text)
            self.memory.add_message(session_id, "assistant", response_text)
            return response_text

        # 3. For contextual RAG queries and multi-turn planning
        response_text = await rag_query(
            user_query=user_text,
            vector_store=self.vector_store,
            gemini_api_key=settings.GEMINI_API_KEY,
            chat_history=history,
            n_results=5
        )
        
        self.memory.add_message(session_id, "user", user_text)
        self.memory.add_message(session_id, "assistant", response_text)
        return response_text
