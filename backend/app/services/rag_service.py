import os
from typing import List, Dict, Optional
import google.generativeai as genai
from ..config import settings
from .vector_store import RouteVectorStore

SYSTEM_PROMPT = """You are the official VIT Chennai Campus Bus AI Assistant.
Your goal is to provide students, faculty, and commuters with precise, grounded, and courteous transit guidance based solely on the verified institutional bus route data provided below.

Strict Guidelines:
1. Always base your answers ONLY on the provided Bus Route Context. Do not invent routes, stops, or timings.
2. If a commuter asks about a location not found in the context, explicitly state that no direct bus serves that stop and recommend the nearest known transit point if available.
3. Always include Route Numbers, Stop Names, and Scheduled Departure Timings clearly.
4. When multiple options exist, compare them concisely (e.g. using bullet points or a brief Markdown table).
5. For accountability inquiries (e.g. "Who drives Route 1?"), provide the driver name, phone number, and route in-charge details accurately.
6. Keep answers informative, concise, and easy to read on mobile or desktop devices.
"""

async def rag_query(
    user_query: str,
    vector_store: RouteVectorStore,
    gemini_api_key: Optional[str] = None,
    chat_history: Optional[List[Dict[str, str]]] = None,
    n_results: int = 5
) -> str:
    """
    RAG Pipeline:
    1. Semantically retrieve relevant bus routes from Vector Store.
    2. Format retrieved documents as grounded context.
    3. Feed context + chat history + user query to Gemini model.
    4. Return AI assistant response.
    """
    api_key = gemini_api_key or settings.GEMINI_API_KEY
    retrieved_docs = vector_store.search(user_query, n_results=n_results)
    
    # Format context
    context_blocks = []
    for i, doc in enumerate(retrieved_docs, start=1):
        context_blocks.append(f"--- ROUTE OPTION {i} ---\n{doc['text']}")
        
    context_str = "\n\n".join(context_blocks) if context_blocks else "No matching route documents found in database."
    
    # Format chat history
    history_str = ""
    if chat_history:
        history_lines = []
        for msg in chat_history[-6:]:  # last 3 turns
            role = "Student" if msg.get("role") == "user" else "Assistant"
            history_lines.append(f"{role}: {msg.get('content', '')}")
        history_str = "\nRecent Conversation History:\n" + "\n".join(history_lines) + "\n"

    prompt = f"""{SYSTEM_PROMPT}

{history_str}
Verified VIT Chennai Bus Route Context:
========================================
{context_str}
========================================

Student Question: {user_query}

Answer:"""

    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(settings.DEFAULT_GEMINI_MODEL)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            # Fallback will take over below
            pass

    # Heuristic fallback if API is not accessible
    if retrieved_docs:
        top_meta = retrieved_docs[0]["metadata"]
        return (
            f"**Route {top_meta.get('route_number')} ({top_meta.get('route_name')})**\n\n"
            f"- **Bus Category**: {top_meta.get('bus_type')}\n"
            f"- **Driver**: {top_meta.get('driver_name')} ({top_meta.get('driver_phone')})\n"
            f"- **In-Charge**: {top_meta.get('incharge_name')} ({top_meta.get('incharge_phone')})\n\n"
            f"Here is the schedule information retrieved for your inquiry:\n"
            f"{retrieved_docs[0]['text']}"
        )
        
    return "I couldn't locate any matching routes for your query. Please check your stop name or contact the campus transport office."
