import os
import pytest
import aiosqlite
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from pathlib import Path

# Configure test environment
os.environ["DATABASE_PATH"] = str(Path(__file__).parent / "test_noto.db")
os.environ["GEMINI_API_KEY"] = "mock-key-for-tests"

from app.main import app
from app.db.database import init_db

@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()
    yield
    test_db = Path(os.environ["DATABASE_PATH"])
    if test_db.exists():
        try:
            test_db.unlink()
        except Exception:
            pass

@pytest.mark.anyio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["app"] == "Noto"
        assert data["status"] == "healthy"

@pytest.mark.anyio
async def test_folder_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create folder
        create_res = await client.post("/api/folders", json={"name": "Projects", "icon": "folder"})
        assert create_res.status_code == 201
        folder = create_res.json()
        folder_id = folder["id"]
        assert folder["name"] == "Projects"

        # 2. List folders
        list_res = await client.get("/api/folders")
        assert list_res.status_code == 200
        folders = list_res.json()
        assert any(f["id"] == folder_id for f in folders)

        # 3. Update folder
        update_res = await client.put(f"/api/folders/{folder_id}", json={"name": "Work Projects"})
        assert update_res.status_code == 200
        assert update_res.json()["name"] == "Work Projects"

        # 4. Delete folder
        del_res = await client.delete(f"/api/folders/{folder_id}")
        assert del_res.status_code == 204

@pytest.mark.anyio
async def test_note_crud_and_fts_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create a note with unique keywords
        create_res = await client.post("/api/notes", json={
            "title": "Quantum Computing Notes",
            "content": "Exploring superposition and quantum entanglement algorithms in Python."
        })
        assert create_res.status_code == 201
        note = create_res.json()
        note_id = note["id"]
        assert note["title"] == "Quantum Computing Notes"

        # 2. Read note
        get_res = await client.get(f"/api/notes/{note_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == note_id

        # 3. Test Full-Text Search (FTS5)
        search_res = await client.get("/api/search?q=entanglement")
        assert search_res.status_code == 200
        results = search_res.json()
        assert len(results) >= 1
        assert results[0]["id"] == note_id
        assert "entanglement" in results[0]["snippet"].lower()

        # 4. Update note
        update_res = await client.put(f"/api/notes/{note_id}", json={
            "title": "Quantum Computing Refined",
            "content": "Updated content with advanced Qiskit workflows."
        })
        assert update_res.status_code == 200
        assert update_res.json()["title"] == "Quantum Computing Refined"

        # 5. Delete note
        del_res = await client.delete(f"/api/notes/{note_id}")
        assert del_res.status_code == 204

@pytest.mark.anyio
async def test_ai_status():
    with patch("app.api.endpoints.ai.llm_service.check_ollama_status", new=AsyncMock(return_value=False)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert "default_provider" in data
    assert "gemini_configured" in data
    assert data["ollama_available"] is False
