import pytest
from app.services.llm import llm_service
from httpx import AsyncClient, ASGITransport
from app.main import app

def test_system_prompt_builder():
    prompt_new = llm_service.build_system_prompt(mode="new_note", tone="bulleted")
    assert "Noto AI" in prompt_new
    assert "Draft a fresh, structured note" in prompt_new
    assert "task checkboxes" in prompt_new

    prompt_tidy = llm_service.build_system_prompt(mode="tidy_note", tone="professional")
    assert "Tidy, refine, and improve" in prompt_tidy
    assert "strictly preserving their factual meaning" in prompt_tidy
    assert "professional" in prompt_tidy

@pytest.mark.anyio
async def test_ai_draft_streaming_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Request with mock provider (mock key set in env)
        payload = {
            "prompt": "Test meeting note",
            "context_content": "Drafting test",
            "mode": "new_note",
            "tone": "balanced",
            "provider": "gemini"
        }
        res = await client.post("/api/ai/draft", json=payload)
        assert res.status_code == 200
        assert "text/event-stream" in res.headers["content-type"]
