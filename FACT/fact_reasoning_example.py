from pydantic import BaseModel, Field
from typing import Optional, List
from sentence_transformers import SentenceTransformer, util

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
    
    def is_fact(self) -> bool:
        """Validate this object represents a true fact."""
        return self.is_verifiable and self.is_objective

fact = Fact(
    statement="R134a has a boiling point of -26.3°C at 1 atm",
    source="ASHRAE Handbook",
    context="Standard pressure conditions"
)

if fact.is_fact():
    # Use in reasoning chain
    reasoning: list[str] = []  # or provided by your reasoning engine
    reasoning.append(fact.statement)
    
model = SentenceTransformer("all-MiniLM-L6-v2")
def semantic_similarity(a: str, b: str) -> float:
    return util.cos_sim(model.encode(a), model.encode(b))[0][0]

def validate_against_fact(claim: str, fact: Fact, threshold: float = 0.9) -> bool:
    # semantic_similarity should be injected or mocked for unit testing.
    score = semantic_similarity(claim, fact.statement)
    return score > threshold and fact.is_fact()

