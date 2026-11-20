
from pydantic import BaseModel, Field


class InterviewScorecard(BaseModel):
    score: int = Field(ge=0, le=10)

    strengths: list[str] = Field(min_length=2, max_length=2)

    gaps: list[str] = Field(min_length=2, max_length=2)

    hint: str

    next_topic: str
