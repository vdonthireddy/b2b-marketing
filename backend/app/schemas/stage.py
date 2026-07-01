from pydantic import BaseModel


class StageCreate(BaseModel):
    name: str
    description: str | None = None
    icon: str = "📌"
    color: str = "#6366f1"
    position: int | None = None


class StageUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None


class StageReorder(BaseModel):
    stage_ids: list[str]  # Ordered list of stage IDs


class StageItemCreate(BaseModel):
    text: str
    content_type: str | None = None


class StageItemUpdate(BaseModel):
    text: str | None = None
    content_type: str | None = None


class StageItemResponse(BaseModel):
    id: str
    text: str
    position: int
    content_type: str | None = None

    model_config = {"from_attributes": True}


class StageResponse(BaseModel):
    id: str
    journey_id: str
    name: str
    description: str | None = None
    icon: str
    color: str
    position: int
    goals: list[StageItemResponse] = []
    touchpoints: list[StageItemResponse] = []
    content: list[StageItemResponse] = []

    model_config = {"from_attributes": True}
