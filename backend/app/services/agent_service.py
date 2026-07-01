import json
import logging
from pydantic import BaseModel, ValidationError, Field
from typing import List
import google.generativeai as genai
from app.config import get_settings
from app.services.journey_service import JourneyService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

settings = get_settings()
logger = logging.getLogger(__name__)

# Pydantic schemas for strict LLM output validation
class LLMGoal(BaseModel):
    text: str = Field(..., description="A specific, actionable goal for this stage.")

class LLMTouchpoint(BaseModel):
    text: str = Field(..., description="A digital or physical touchpoint.")

class LLMContent(BaseModel):
    text: str = Field(..., description="A specific piece of content.")
    content_type: str = Field(..., description="Type of content, e.g., 'email', 'blog', 'video', 'pdf'")

class LLMStage(BaseModel):
    name: str = Field(..., description="Name of the stage, e.g., 'Awareness', 'Engagement'")
    description: str = Field(..., description="Brief description of what happens in this stage.")
    goals: List[LLMGoal] = Field(min_length=1, description="List of goals for this stage.")
    touchpoints: List[LLMTouchpoint] = Field(min_length=1, description="List of touchpoints.")
    content: List[LLMContent] = Field(min_length=1, description="List of content items.")

class LLMJourney(BaseModel):
    name: str = Field(..., description="Name of the generated journey.")
    description: str = Field(..., description="Brief description of the journey.")
    stages: List[LLMStage] = Field(min_length=4, description="List of stages in sequential order. Must be at least 4 stages.")


import httpx

class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.use_ollama = settings.use_ollama
        self.ollama_url = settings.ollama_url
        self.ollama_model = settings.ollama_model

        if not self.use_ollama and settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(
                "gemini-2.0-flash", 
                generation_config={"response_mime_type": "application/json"}
            )
        else:
            self.model = None

    def _ensure_available(self):
        if not self.use_ollama and not self.model:
            raise HTTPException(status_code=503, detail="AI service not configured. Missing GEMINI_API_KEY in environment.")

    async def _generate_ollama(self, messages_or_prompt: list, system_prompt: str = "") -> str:
        ollama_messages = []
        if system_prompt:
            ollama_messages.append({"role": "system", "content": system_prompt})
            
        for msg in messages_or_prompt:
            role = msg["role"]
            if role == "model":
                role = "assistant"
            
            content = ""
            if "parts" in msg:
                content = "\n".join(msg["parts"])
            elif "content" in msg:
                content = msg["content"]
            ollama_messages.append({"role": role, "content": content})

        payload = {
            "model": self.ollama_model,
            "messages": ollama_messages,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 2048
            }
        }

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
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

    async def generate_and_save_journey(self, prompt_text: str, team_id: str, user_id: str):
        system_prompt = """
        You are an elite B2B marketing agent. You autonomously create complete customer journey maps.
        The user will give you a prompt. You MUST return a JSON object representing the journey.
        The JSON must match this structure exactly:
        {
          "name": "Journey Name",
          "description": "Brief summary",
          "stages": [
            {
              "name": "Stage Name",
              "description": "What happens here",
              "goals": [{"text": "..."}],
              "touchpoints": [{"text": "..."}],
              "content": [{"text": "...", "content_type": "..."}]
            }
          ]
        }
        Requirements:
        1. Produce exactly 4 stages in the list. Even if the user request is simple, structure it into 4 sequential stages (e.g. Stage 1: Introduction, Stage 2: Wait & Nurture, Stage 3: Conversion/Offer, Stage 4: Follow-up/Onboarding).
        2. Provide at least 1 goal, touchpoint, and content per stage.
        3. Only output valid JSON without any markdown code fences or backticks.
        """

        messages = [
            {"role": "user", "parts": [system_prompt + "\n\nUser Prompt: " + prompt_text]}
        ]

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            logger.info(f"Agent Loop Attempt {attempt + 1}")
            try:
                if self.use_ollama:
                    response_text = await self._generate_ollama(messages, system_prompt)
                else:
                    self._ensure_available()
                    response = self.model.generate_content(messages)
                    response_text = response.text
                
                # 1. Parse JSON
                try:
                    data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse JSON: {str(e)}. Ensure your output is purely JSON without markdown backticks."
                    if self.use_ollama:
                        messages.append({"role": "assistant", "content": response_text})
                        messages.append({"role": "user", "content": error_msg})
                    else:
                        messages.append({"role": "model", "parts": [response_text]})
                        messages.append({"role": "user", "parts": [error_msg]})
                    last_error = error_msg
                    continue
                
                # 2. Validate structure with Pydantic
                try:
                    validated_journey = LLMJourney(**data)
                except ValidationError as e:
                    error_msg = f"JSON structure invalid against schema: {e.json()}. Please fix these errors and try again."
                    if self.use_ollama:
                        messages.append({"role": "assistant", "content": response_text})
                        messages.append({"role": "user", "content": error_msg})
                    else:
                        messages.append({"role": "model", "parts": [response_text]})
                        messages.append({"role": "user", "parts": [error_msg]})
                    last_error = error_msg
                    continue
                
                # 3. If validation passed, save to DB
                logger.info("Agent successfully validated journey structure. Saving to database...")
                return await self._save_journey(validated_journey, team_id, user_id)

            except Exception as e:
                logger.error(f"Error communicating with LLM: {str(e)}")
                raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")

        # If we exit the loop, we failed
        logger.error(f"Agent loop failed after {max_retries} retries. Last error: {last_error}")
        raise HTTPException(status_code=422, detail=f"Agent failed to generate a valid journey. Last error: {last_error}")

    async def _save_journey(self, llm_journey: LLMJourney, team_id: str, user_id: str):
        journey_service = JourneyService(self.db)
        
        # 1. Create Journey (no default stages)
        journey = await journey_service.create_journey(
            team_id=team_id, 
            user_id=user_id, 
            name=llm_journey.name, 
            description=llm_journey.description,
            include_default_stages=False
        )
        
        # 2. Create Stages and nested items
        for i, stg in enumerate(llm_journey.stages):
            # Using defaults for icon/color since the prompt doesn't ask for them to keep it simple
            stage_db = await journey_service.add_stage(
                journey_id=journey.id,
                team_id=team_id,
                user_id=user_id,
                name=stg.name,
                description=stg.description,
                position=i
            )
            
            # Add goals
            for g in stg.goals:
                await journey_service.add_stage_item(stage_db.id, team_id, "goal", g.text)
            
            # Add touchpoints
            for t in stg.touchpoints:
                await journey_service.add_stage_item(stage_db.id, team_id, "touchpoint", t.text)
                
            # Add content
            for c in stg.content:
                await journey_service.add_stage_item(stage_db.id, team_id, "content", c.text, c.content_type)
                
        # Expunge the journey from the session to force a complete re-fetch with relationships
        self.db.expunge(journey)
        
        # Return full loaded journey
        return await journey_service.get_journey(journey.id, team_id)
