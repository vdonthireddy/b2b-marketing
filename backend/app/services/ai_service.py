import google.generativeai as genai
from app.config import get_settings
from fastapi import HTTPException
import json

settings = get_settings()


class AIService:
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
        else:
            self.model = None

    def _ensure_available(self):
        if not self.model:
            raise HTTPException(
                status_code=503,
                detail="AI service not available. Configure GEMINI_API_KEY in .env"
            )

    async def suggest_goals(self, stage_name: str, journey_context: str = "") -> list[str]:
        """Suggest customer goals for a given journey stage."""
        self._ensure_available()

        prompt = f"""You are a B2B marketing expert. For a customer journey stage called "{stage_name}",
suggest 5 specific, actionable customer goals.

Journey context: {journey_context or 'General B2B SaaS product'}

Return ONLY a JSON array of strings, no other text. Example:
["Goal 1", "Goal 2", "Goal 3", "Goal 4", "Goal 5"]"""

        response = self.model.generate_content(prompt)
        return self._parse_json_array(response.text)

    async def suggest_touchpoints(self, stage_name: str, journey_context: str = "") -> list[str]:
        """Suggest digital touchpoints for a journey stage."""
        self._ensure_available()

        prompt = f"""You are a B2B marketing expert. For a customer journey stage called "{stage_name}",
suggest 5 digital touchpoints (channels, platforms, interactions) that customers use.

Journey context: {journey_context or 'General B2B SaaS product'}

Return ONLY a JSON array of strings, no other text."""

        response = self.model.generate_content(prompt)
        return self._parse_json_array(response.text)

    async def suggest_content(self, stage_name: str, journey_context: str = "") -> list[str]:
        """Suggest content types appropriate for a journey stage."""
        self._ensure_available()

        prompt = f"""You are a B2B content marketing expert. For a customer journey stage called "{stage_name}",
suggest 5 specific content types or formats that would be effective.

Journey context: {journey_context or 'General B2B SaaS product'}

Return ONLY a JSON array of strings, no other text."""

        response = self.model.generate_content(prompt)
        return self._parse_json_array(response.text)

    async def suggest_persona(self, industry: str = "", role: str = "") -> dict:
        """Suggest persona details based on industry and role."""
        self._ensure_available()

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

        response = self.model.generate_content(prompt)
        return self._parse_json_object(response.text)

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
