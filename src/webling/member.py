from datetime import date
from pydantic import AliasPath, BaseModel, Field


class Member(BaseModel):
    talent: bool = Field(validation_alias=AliasPath('properties', 'Talent'))
    start: date = Field(validation_alias=AliasPath('properties', 'Eintrittsdatum'))
    end: date | None = Field(default=None, validation_alias=AliasPath('properties', 'Austrittsdatum'))

    def is_active(self, year: int) -> bool:
        return self.start.year <= year and (self.end is None or year < self.end.year)