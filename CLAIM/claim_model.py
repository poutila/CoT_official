from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class Claim(BaseModel):
    """A statement proposed to be true, subject to validation."""
    id: Optional[str] = Field(None, description="Optional unique identifier (UUID, hash, etc.)")
    type: Literal["Claim"] = Field(default="Claim", description="Identifier for this object type")
    statement: str = Field(..., description="The content of the claim")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score between 0 and 1")
    source: Optional[str] = Field(None, description="Optional source or reference")
    context: Optional[str] = Field(None, description="Context in which the claim holds")
    tags: Optional[List[str]] = Field(default_factory=list, description="Optional topic tags")