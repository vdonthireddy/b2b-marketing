import google.generativeai as genai
from app.config import get_settings
from fastapi import HTTPException
import json
import httpx

settings = get_settings()


class AIService:
    def __init__(self):
        self.use_ollama = settings.use_ollama
        self.ollama_url = settings.ollama_url
        self.ollama_model = settings.ollama_model

        if not self.use_ollama and settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
        else:
            self.model = None

    def _ensure_available(self):
        if not self.use_ollama and not self.model:
            raise HTTPException(
                status_code=503,
                detail="AI service not available. Configure GEMINI_API_KEY in .env"
            )

    async def _generate_ollama(self, prompt: str, is_json: bool = False) -> str:
        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 2048
            }
        }
        if is_json:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(f"{self.ollama_url}/api/chat", json=payload)
                if resp.status_code != 200:
                    raise HTTPException(
                        status_code=resp.status_code,
                        detail=f"Ollama returned error: {resp.text}"
                    )
                return resp.json()["message"]["content"]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to communicate with Ollama: {str(e)}"
            )

    async def suggest_goals(self, stage_name: str, journey_context: str = "") -> list[str]:
        """Suggest customer goals for a given journey stage."""
        prompt = f"""You are a B2B marketing expert. For a customer journey stage called "{stage_name}",
suggest 5 specific, actionable customer goals.

Journey context: {journey_context or 'General B2B SaaS product'}

Return ONLY a JSON array of strings, no other text. Example:
["Goal 1", "Goal 2", "Goal 3", "Goal 4", "Goal 5"]"""

        if self.use_ollama:
            text = await self._generate_ollama(prompt, is_json=True)
        else:
            self._ensure_available()
            response = self.model.generate_content(prompt)
            text = response.text
        return self._parse_json_array(text)

    async def suggest_touchpoints(self, stage_name: str, journey_context: str = "") -> list[str]:
        """Suggest digital touchpoints for a journey stage."""
        prompt = f"""You are a B2B marketing expert. For a customer journey stage called "{stage_name}",
suggest 5 digital touchpoints (channels, platforms, interactions) that customers use.

Journey context: {journey_context or 'General B2B SaaS product'}

Return ONLY a JSON array of strings, no other text."""

        if self.use_ollama:
            text = await self._generate_ollama(prompt, is_json=True)
        else:
            self._ensure_available()
            response = self.model.generate_content(prompt)
            text = response.text
        return self._parse_json_array(text)

    async def suggest_content(self, stage_name: str, journey_context: str = "") -> list[str]:
        """Suggest content types appropriate for a journey stage."""
        prompt = f"""You are a B2B content marketing expert. For a customer journey stage called "{stage_name}",
suggest 5 specific content types or formats that would be effective.

Journey context: {journey_context or 'General B2B SaaS product'}

Return ONLY a JSON array of strings, no other text."""

        if self.use_ollama:
            text = await self._generate_ollama(prompt, is_json=True)
        else:
            self._ensure_available()
            response = self.model.generate_content(prompt)
            text = response.text
        return self._parse_json_array(text)

    async def suggest_persona(self, industry: str = "", role: str = "") -> dict:
        """Suggest persona details based on industry and role."""
        prompt = f"""You are a B2B marketing expert. Create a buyer persona for:
Industry: {industry or 'Technology/SaaS'}
Role: {role or 'Marketing Manager'}

Return ONLY a JSON object with these fields:
{{
  "name": "A realistic name",
  "role_title": "Job title",
  "company_size": "SMB or Mid-Market or Enterprise",
  "goals": "2-3 key goals, separated by newlines",
  "pain_points": "2-3 pain points, separated by newlines",
  "motivations": "2-3 motivations, separated by newlines"
}}"""

        if self.use_ollama:
            text = await self._generate_ollama(prompt, is_json=True)
        else:
            self._ensure_available()
            response = self.model.generate_content(prompt)
            text = response.text
        return self._parse_json_object(text)

    def _parse_json_array(self, text: str) -> list[str]:
        """Extract a JSON array from model response text."""
        try:
            # Try direct parse
            cleaned = text.strip()
            if cleaned.startswith("```"):
                # Remove markdown code fences
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(cleaned)
        except (json.JSONDecodeError, IndexError):
            # Fallback: split by newlines
            lines = [l.strip().strip("-•*").strip() for l in text.strip().split("\n") if l.strip()]
            return lines[:5]

    def _parse_json_object(self, text: str) -> dict:
        """Extract a JSON object from model response text."""
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(cleaned)
        except (json.JSONDecodeError, IndexError):
            return {
                "name": "Sample Persona",
                "role_title": "Marketing Manager",
                "company_size": "Mid-Market",
                "goals": "Increase pipeline\nImprove attribution",
                "pain_points": "Lack of data\nSiloed teams",
                "motivations": "Career growth\nTeam efficiency",
            }
