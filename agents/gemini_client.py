# agents/gemini_client.py
import os
import asyncio
from typing import Optional
from dotenv import load_dotenv

# google-generativeai SDK
# pip install --upgrade google-generativeai
import google.generativeai as genai  # type: ignore

load_dotenv()

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY missing in .env")

        # Configure and create model (type: ignore to quiet Pylance false positives)
        genai.configure(api_key=self.api_key)  # type: ignore[attr-defined]
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")  # type: ignore[attr-defined]

    async def generate_content_async(self, prompt: str) -> str:
        try:
            # run blocking SDK call in threadpool
            resp = await asyncio.to_thread(self.model.generate_content, prompt)
            # the SDK returns an object with .text in typical usage
            return resp.text.strip() if getattr(resp, "text", None) else str(resp)
        except Exception as e:
            return f"❌ Gemini API error: {str(e)}"