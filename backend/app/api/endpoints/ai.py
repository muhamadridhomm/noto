import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ...models.schemas import AIDraftRequest, AISettingsResponse
from ...services.llm import llm_service
from ...core.config import settings

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/status", response_model=AISettingsResponse)
async def get_ai_status():
    ollama_ok = await llm_service.check_ollama_status()
    return AISettingsResponse(
        default_provider=settings.DEFAULT_PROVIDER,
        gemini_configured=bool(settings.GEMINI_API_KEY.strip()),
        gemini_model=settings.GEMINI_MODEL,
        ollama_url=settings.OLLAMA_BASE_URL,
        ollama_model=settings.OLLAMA_MODEL,
        ollama_available=ollama_ok
    )

@router.post("/draft")
async def stream_draft(req: AIDraftRequest):
    """
    Streams the generated note draft using Server-Sent Events (SSE).
    The AI acts strictly as a drafter; the client receives the stream,
    renders it in a review drawer, and only saves when the user clicks 'Approve'.
    """
    async def event_generator():
        async for chunk in llm_service.stream_draft(
            prompt=req.prompt,
            context_content=req.context_content or "",
            mode=req.mode,
            tone=req.tone or "balanced",
            provider=req.provider
        ):
            # Send SSE data frame
            data = json.dumps({"text": chunk})
            yield f"data: {data}\n\n"
        
        # End of stream event
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
