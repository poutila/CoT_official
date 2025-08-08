from sentence_transformers import SentenceTransformer, util
from typing import Optional, List
from pydantic import BaseModel, Field

class Assumption(BaseModel):
    id: Optional[str] = Field(None)
    type: str = Field("Assumption", const=True)
    statement: str = Field(...)
    scope: Optional[str] = Field(None)
    tags: Optional[List[str]] = Field(default_factory=list)

    def is_assumption(self) -> bool:
        return bool(self.statement)

assumption = Assumption(
    statement="The system has access to an uninterrupted power supply.",
    scope="During test conditions in lab environment"
)

if assumption.is_assumption():
    reasoning: list[str] = []
    reasoning.append(assumption.statement)

model = SentenceTransformer("all-MiniLM-L6-v2")
def semantic_similarity(a: str, b: str) -> float:
    return util.cos_sim(model.encode(a), model.encode(b))[0][0]

def validate_against_assumption(assumption: Assumption, reference: str, threshold: float = 0.9) -> bool:
    score = semantic_similarity(assumption.statement, reference)
    return score > threshold