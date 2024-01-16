from datetime import date
from pydantic import AliasPath, BaseModel, Field
from enum import Enum


class MemberGroup(BaseModel):
    name: str = Field(validation_alias=AliasPath('properties', 'title'))
    members: list[int] = Field(validation_alias=AliasPath('children', 'member'))
    

class Status(str, Enum):
    Aspirant = 'Aspirant'
    Aktiv = 'Aktiv'
    Ausgetreten = 'Ausgetreten'


class Member(BaseModel):
    talent: bool = Field(validation_alias=AliasPath('properties', 'Talent'))
    status: Status = Field(validation_alias=AliasPath('properties', 'Status'))
    start: date = Field(validation_alias=AliasPath('properties', 'Eintrittsdatum'))
    end: date | None = Field(default=None, validation_alias=AliasPath('properties', 'Austrittsdatum'))

    def is_active(self, year: int) -> bool:
        if self.status == Status.Aspirant:
            return False
        return self.start.year <= year and (self.end is None or year < self.end.year)

    def joined(self, year: int) -> bool:
        if self.status == Status.Aspirant:
            return False
        return self.start.year == year

    def left(self, year: int) -> bool:
        return self.end != None and self.end.year == year