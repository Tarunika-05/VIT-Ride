import time
from fastapi import APIRouter, HTTPException, Request
from ..models.route import ChatRequest, ChatResponse
from ..services.memory import memory_manager

router = APIRouter(tags=["AI Assistant"])

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(payload: ChatRequest, request: Request):
    """
    Interact with the conversational AI transit assistant.
    Processes the inquiry using LangGraph, RAG, and tools with latency instrumentation.
    """
    agent = getattr(request.app.state, "agent", None)
    if agent is None:
        raise HTTPException(status_code=503, detail="Transit Agent is initializing. Please try again shortly.")

    start_time = time.time()
    try:
        response_text = await agent.chat(payload.message, session_id=payload.session_id)
        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
        return ChatResponse(
            response=response_text,
            session_id=payload.session_id,
            response_time_ms=elapsed_ms
        )
    except Exception as e:
        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
        return ChatResponse(
            response=f"I encountered a temporary issue processing your transit query: {str(e)}",
            session_id=payload.session_id,
            response_time_ms=elapsed_ms
        )

@router.delete("/chat/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Reset conversation history for the given session ID.
    """
    memory_manager.clear(session_id)
    return {"status": "cleared", "session_id": session_id}

@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Retrieve message history for the given session ID.
    """
    return {"session_id": session_id, "history": memory_manager.get_history(session_id)}
