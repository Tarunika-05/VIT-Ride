import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from .config import settings
from .services.route_service import load_routes
from .services.vector_store import RouteVectorStore
from .services.agent import TransitAgent
from .routers.routes import router as routes_router
from .routers.chat import router as chat_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vit_transit_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    logger.info("Initializing VIT Campus Transit Backend...")
    try:
        # 1. Load routes
        routes = load_routes(force_reload=True)
        app.state.routes = routes
        logger.info(f"Loaded {len(routes)} bus routes into memory.")
        
        # 2. Vector store & RAG indexing
        vector_store = RouteVectorStore()
        indexed_count = vector_store.index_routes(routes)
        app.state.vector_store = vector_store
        logger.info(f"Indexed {indexed_count} route documents in vector store.")
        
        # 3. Transit Agent
        agent = TransitAgent(vector_store=vector_store)
        app.state.agent = agent
        logger.info("Transit AI Agent initialized and ready.")
        
    except Exception as e:
        logger.error(f"Error during startup initialization: {e}", exc_info=True)
        
    yield
    # --- SHUTDOWN ---
    logger.info("Shutting down VIT Campus Transit Backend.")

app = FastAPI(
    title="VIT Chennai Campus Transit AI",
    description="Intelligent Campus Bus Route Finder & AI Decision Support System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(routes_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "VIT Campus Transit AI",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
