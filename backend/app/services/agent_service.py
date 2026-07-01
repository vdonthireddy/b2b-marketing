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


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(
                "gemini-2.0-flash", 
                generation_config={"response_mime_type": "application/json"}
            )
        else:
            self.model = None

    async def generate_and_save_journey(self, prompt_text: str, team_id: str, user_id: str):
        if not self.model:
            raise HTTPException(status_code=503, detail="AI service not configured. Missing GEMINI_API_KEY in environment.")
        
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
        1. Produce at least 4 stages.
        2. Provide at least 1 goal, touchpoint, and content per stage.
        3. Only output valid JSON.
        """

        messages = [
            {"role": "user", "parts": [system_prompt + "\n\nUser Prompt: " + prompt_text]}
        ]

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            logger.info(f"Agent Loop Attempt {attempt + 1}")
            try:
                response = self.model.generate_content(messages)
                response_text = response.text
                
                # 1. Parse JSON
                try:
                    data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse JSON: {str(e)}. Ensure your output is purely JSON without markdown backticks."
                    messages.append({"role": "model", "parts": [response_text]})
                    messages.append({"role": "user", "parts": [error_msg]})
                    last_error = error_msg
                    continue
                
                # 2. Validate structure with Pydantic
                try:
                    validated_journey = LLMJourney(**data)
                except ValidationError as e:
                    error_msg = f"JSON structure invalid against schema: {e.json()}. Please fix these errors and try again."
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
