from pydantic import BaseModel, Field
from typing import Optional, List

class Assumption(BaseModel):
    """An unverified but accepted premise for reasoning."""
    id: Optional[str] = Field(None, description="Optional unique identifier (UUID, hash, etc.)")
    type: str = Field("Assumption", const=True, description="Identifier for this object type")
    statement: str = Field(..., description="The content of the assumption")
    scope: Optional[str] = Field(None, description="Context in which the assumption is accepted")
    tags: Optional[List[str]] = Field(default_factory=list, description="Optional topic tags")