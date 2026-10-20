import json
import httpx
from typing import AsyncGenerator, Optional
from ..core.config import settings

class LLMService:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY
        self.gemini_model = settings.GEMINI_MODEL
        self.ollama_url = settings.OLLAMA_BASE_URL.rstrip('/')
        self.ollama_model = settings.OLLAMA_MODEL

    async def check_ollama_status(self) -> bool:
        """Check if local Ollama server is reachable."""
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.ollama_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def build_system_prompt(self, mode: str, tone: str) -> str:
        base = (
            "You are Noto AI, an intelligent, precise note-taking assistant. "
            "Your output will be presented to the user as a draft note formatted in clean Markdown. "
            "Never include meta-commentary like 'Sure, here is your note:' or 'Hope this helps!'. "
            "Output ONLY the note content itself."
        )
        
        tone_instructions = {
            "concise": "Keep the content very concise, punchy, and minimal. Focus on core bullet points.",
            "professional": "Use professional, structured phrasing with clear executive summary and action items.",
            "bulleted": "Format details as scannable bullet points and task checkboxes (- [ ] task).",
            "balanced": "Maintain a natural, organized, and clean tone with clear headers and bullet points where helpful."
        }.get(tone, "Maintain a clean, organized markdown format.")

        if mode == "new_note":
            return (
                f"{base}\n\nTask: Draft a fresh, structured note based on the user's prompt or rough ideas. "
                f"Include a top-level `# Note Title`, followed by organized sections, key takeaways, and action items if applicable. "
                f"Tone instruction: {tone_instructions}"
            )
        elif mode == "tidy_note":
            return (
                f"{base}\n\nTask: Tidy, refine, and improve the user's existing note or text while strictly preserving their factual meaning and intent. "
                f"Fix spelling, grammar, flow, and formatting into clean Markdown with clear headings and lists. "
                f"Tone instruction: {tone_instructions}"
            )
        else:
            return f"{base}\n\nTask: Follow the user's instructions to refine or create note content.\nTone instruction: {tone_instructions}"

    async def stream_gemini(self, prompt: str, system_prompt: str) -> AsyncGenerator[str, None]:
        """Streams text chunks from Google Gemini API using REST SSE streaming."""
        if not self.gemini_key:
            yield "⚠️ Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file or choose Ollama in settings."
            return

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:streamGenerateContent?alt=sse&key={self.gemini_key}"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "temperature": 0.4,
                "topP": 0.95
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", url, json=payload, headers={"Content-Type": "application/json"}) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        yield f"\n⚠️ Gemini API Error ({response.status_code}): {err_text.decode('utf-8', errors='ignore')}"
                        return

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            candidates = chunk_data.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                for p in parts:
                                    if "text" in p:
                                        yield p["text"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"\n⚠️ Connection error while contacting Gemini API: {str(e)}"

    async def stream_ollama(self, prompt: str, system_prompt: str) -> AsyncGenerator[str, None]:
        """Streams text chunks from local Ollama endpoint."""
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True,
            "options": {
                "temperature": 0.4
            }
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        yield f"\n⚠️ Ollama Error ({response.status_code}): {err_text.decode('utf-8', errors='ignore')}"
                        return

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk_data = json.loads(line)
                            if "response" in chunk_data:
                                yield chunk_data["response"]
                            if chunk_data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"\n⚠️ Could not connect to local Ollama at {self.ollama_url}. Is Ollama running? ({str(e)})"

    async def stream_draft(
        self,
        prompt: str,
        context_content: str = "",
        mode: str = "new_note",
        tone: str = "balanced",
        provider: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Unified streaming interface selecting between Gemini and Ollama."""
        selected_provider = provider or settings.DEFAULT_PROVIDER
        system_prompt = self.build_system_prompt(mode, tone)
        
        full_user_input = prompt
        if context_content and context_content.strip():
            full_user_input = (
                f"User Instruction:\n{prompt}\n\n"
                f"Existing Note Content to work with:\n---\n{context_content}\n---"
            )

        if selected_provider.lower() == "ollama":
            async for chunk in self.stream_ollama(full_user_input, system_prompt):
                yield chunk
        else:
            async for chunk in self.stream_gemini(full_user_input, system_prompt):
                yield chunk

llm_service = LLMService()
