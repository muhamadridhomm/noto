from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db.database import init_db
from .api.endpoints import folders, notes, search, ai

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure database and tables exist
    await init_db()
    yield
    # Shutdown logic if needed

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS setup for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Local-first app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(folders.router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(ai.router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "Noto",
        "version": settings.VERSION
    }
