from pydantic import BaseModel, Field
from typing import List


class YearStats(BaseModel):
    year: int = Field(description="Year of the stats")
    active_members: int = Field(description="Number of active members")
    talent_members: int = Field(description="Number of talent members")
    new_members: int = Field(description="Number of new members")
    left_members: int = Field(description="Number of left members")
    heart_rates: List[int] = Field(description="Heart rates of active members")
