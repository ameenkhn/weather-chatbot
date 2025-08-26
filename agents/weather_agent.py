import os
import re
import json
import asyncio
from typing import Dict, List, Tuple, Any, Optional

import requests
from dotenv import load_dotenv

from .gemini_client import GeminiClient

load_dotenv()


class WeatherAgent:
    def __init__(self):
        self.gemini = GeminiClient()
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.weather_api_key:
            raise ValueError("❌ OPENWEATHER_API_KEY missing in .env")

    # ------------------------- Helpers -------------------------
    def _extract_city(self, message: str) -> Optional[str]:
        """
        Extracts city from a user message with simple heuristics:
        - Try "... in <city>"
        - Otherwise take the last comma-separated or space-separated chunk
        """
        msg = message.strip()

        # Try 'in <city>' pattern
        m = re.search(r"\bin\s+([A-Za-z\s\-\.\,']+)$", msg, flags=re.IGNORECASE)
        if m:
            city = m.group(1).strip(" .,'")
            return city if city else None

        # If comma separated, take the last part
        if "," in msg:
            last = msg.split(",")[-1].strip(" .,'")
            if last:
                return last

        # Otherwise take the last word-ish chunk
        parts = re.split(r"\s+", msg)
        if parts:
            candidate = parts[-1].strip(" .,'")
            if candidate and candidate.lower() not in {"weather", "forecast"}:
                return candidate

        return None

    def _fetch_openweather(self, city: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Synchronous HTTP (wrapped in thread by caller) -> returns (data, error)."""
        url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={self.weather_api_key}&units=metric"
        )
        try:
            r = requests.get(url, timeout=8)
            if r.status_code != 200:
                try:
                    err = r.json().get("message", f"HTTP {r.status_code}")
                except Exception:
                    err = f"HTTP {r.status_code}"
                return None, f"OpenWeather error for '{city}': {err}"
            return r.json(), None
        except Exception as e:
            return None, f"OpenWeather request failed: {str(e)}"

    async def _get_openweather(self, city: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Async wrapper around requests."""
        return await asyncio.to_thread(self._fetch_openweather, city)

    # ------------------------- Public API -------------------------
    async def get_response(self, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Uses OpenWeather for real data and Gemini to compose a reply.
        Returns: {"response": str, "tools_used": List[str]}
        """
        tools_used: List[str] = []

        # --- Small-talk detection ---
        if any(word in message.lower() for word in ["hello", "hi", "hey", "how are you", "good morning", "good evening"]):
            tools_used.append("Gemini")
            convo = "\n".join(f"{m['role'].title()}: {m['content']}" for m in history[-6:])
            prompt = (
                "You are a friendly AI assistant. "
                "The user just greeted you or asked a casual question. "
                "Reply naturally, warmly, and conversationally (not too long).\n\n"
                f"Conversation so far:\n{convo}\n\n"
                f"User message: {message}"
            )
            try:
                reply = await self.gemini.generate_content_async(prompt)
            except Exception as e:
                reply = f"Hello! (Gemini error: {e})"
            return {"response": reply, "tools_used": tools_used}

        # --- Weather Query ---
        city = self._extract_city(message) or "New York"  # safe default
        weather_data, weather_err = await self._get_openweather(city)

        if weather_err or not weather_data:
            tools_used.append("Gemini")
            prompt = (
                "You are a helpful weather assistant.\n"
                f"User message: {message}\n"
                f"Weather lookup failed with error: {weather_err}\n"
                "Politely explain the issue and suggest checking the city name. "
                "Offer examples like 'What's the weather in London?' or 'Weather in Mumbai'."
            )
            try:
                reply = await self.gemini.generate_content_async(prompt)
            except Exception as e:
                reply = f"Sorry, I couldn’t fetch the weather. (Gemini error: {e})"
            return {"response": reply, "tools_used": tools_used}

        # Extract useful fields safely
        try:
            name = weather_data.get("name") or city
            weather_list = weather_data.get("weather") or [{}]
            weather = weather_list[0] if isinstance(weather_list, list) else {}
            main = weather_data.get("main") or {}
            wind = weather_data.get("wind") or {}
            sys = weather_data.get("sys") or {}
            dt = weather_data.get("dt")

            desc = str(weather.get("description", "N/A")).capitalize()
            temp = main.get("temp", "N/A")
            feels = main.get("feels_like", "N/A")
            humidity = main.get("humidity", "N/A")
            wind_speed = wind.get("speed", "N/A")
            country = sys.get("country", "")
        except Exception:
            name, desc, temp, feels, humidity, wind_speed, country, dt = city, "N/A", "N/A", "N/A", "N/A", "N/A", "", None

        tools_used.extend(["OpenWeather", "Gemini"])

        convo = "\n".join(f"{m['role'].title()}: {m['content']}" for m in history[-6:])
        weather_summary = {
            "city": name,
            "country": country,
            "description": desc,
            "temperature_c": temp,
            "feels_like_c": feels,
            "humidity_percent": humidity,
            "wind_speed_mps": wind_speed,
            "unix_time": dt,
        }

        prompt = (
            "You are a friendly weather assistant. "
            "Use the provided real-time weather data to answer the user's message naturally.\n\n"
            f"Conversation context (last turns):\n{convo}\n\n"
            f"User message: {message}\n\n"
            f"Real-time weather data (JSON):\n{json.dumps(weather_summary, ensure_ascii=False)}\n\n"
            "Guidelines:\n"
            "- Start with a concise summary (city, condition, temp, feels-like).\n"
            "- Include one helpful tip (e.g., clothing, umbrella, hydration) if relevant.\n"
            "- Keep it friendly and under 100 words.\n"
        )

        try:
            reply = await self.gemini.generate_content_async(prompt)
        except Exception as e:
            reply = f"The weather in {name}: {desc}, {temp}°C (Gemini error: {e})"

        return {"response": reply, "tools_used": tools_used}