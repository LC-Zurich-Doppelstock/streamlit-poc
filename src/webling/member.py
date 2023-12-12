from datetime import date
from pydantic import AliasPath, BaseModel, Field


class Member(BaseModel):
    status: str = Field(validation_alias=AliasPath('properties', 'Status'))
    start: date = Field(validation_alias=AliasPath('properties', 'Eintrittsdatum'))
    end: date | None = Field(default=None, validation_alias=AliasPath('properties', 'Austrittsdatum'))

    def is_active(self, year: int) -> bool:
        return self.start.year <= year and (self.end is None or self.end.year >= year)
    
    @property
    def is_talent(self) -> bool:
        return self.status == 'Talent'