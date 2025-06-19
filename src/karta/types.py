from pydantic import BaseModel, Field
from typing import Optional

class Entity(BaseModel):
    text: str = Field(..., description="The exact text of the entity.")
    label: str = Field(..., description="The category of the entity (e.g., 'PERSON', 'GPE').")
    start_char: int = Field(..., description="The starting character index.")
    end_char: int = Field(..., description="The ending character index.")

class Fact(BaseModel):
    entity: str = Field(..., description="The subject of the fact.")
    attribute: str = Field(..., description="The property of the entity.")
    value: str = Field(..., description="The value of the attribute.")
    source: Optional[str] = Field(None, description="The source from which this fact was derived.")
