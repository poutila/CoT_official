from pydantic import BaseModel, Field
from typing import Optional, List

class Fact(BaseModel):
    """
    A fact is a verifiable, objective statement used as a reliable premise
    within a reasoning chain. It can be checked independently of belief or intent.
    """

    id: Optional[str] = Field(None, description="Optional unique identifier (UUID, hash, etc.)")
    type: str = Field("Fact", const=True, description="Identifier for this object type")
    statement: str = Field(..., description="The factual content in natural language")
    is_verifiable: bool = Field(..., description="True if the fact can be empirically verified")
    is_objective: bool = Field(..., description="True if the fact is not subject to opinion")
    source: Optional[str] = Field(None, description="Optional citation, reference, or authority")
    context: Optional[str] = Field(None, description="Optional condition where the fact applies")
    tags: Optional[List[str]] = Field(default_factory=list, description="Optional topic tags (e.g., physics, history)")