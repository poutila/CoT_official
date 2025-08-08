from sentence_transformers import SentenceTransformer, util
from typing import Optional, List
from pydantic import BaseModel, Field

class Claim(BaseModel):
    id: Optional[str] = Field(None)
    type: str = Field("Claim", const=True)
    statement: str = Field(...)
    confidence: Optional[float] = Field(None, ge=0, le=1)
    source: Optional[str] = Field(None)
    context: Optional[str] = Field(None)
    tags: Optional[List[str]] = Field(default_factory=list)

    def is_claim(self) -> bool:
        return bool(self.statement)

claim = Claim(
    statement="Humans will reach Mars by 2050.",
    confidence=0.8,
    source="Expert forecast 2023",
    context="Assuming continuous investment in space tech"
)

if claim.is_claim():
    reasoning: list[str] = []
    reasoning.append(claim.statement)

model = SentenceTransformer("all-MiniLM-L6-v2")
def semantic_similarity(a: str, b: str) -> float:
    return util.cos_sim(model.encode(a), model.encode(b))[0][0]

def validate_against_claim(claim: Claim, reference: str, threshold: float = 0.9) -> bool:
    score = semantic_similarity(claim.statement, reference)
    return score > threshold