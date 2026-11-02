from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db.database import init_db
from .api.endpoints import folders, notes, search, ai, export

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
for router in (folders.router, notes.router, search.router, ai.router, export.router):
    app.include_router(router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "app": "Noto", "version": settings.VERSION}

FRONTEND_DIST = __import__("os").path.abspath(__import__("os").path.join(__import__("os").path.dirname(__file__), "../../frontend/dist"))
if __import__("os").path.exists(FRONTEND_DIST):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    assets_dir = __import__("os").path.join(FRONTEND_DIST, "assets")
    if __import__("os").path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        candidate = __import__("os").path.join(FRONTEND_DIST, full_path)
        if full_path and __import__("os").path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(__import__("os").path.join(FRONTEND_DIST, "index.html"))
