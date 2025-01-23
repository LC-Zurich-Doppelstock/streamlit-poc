from pydantic import BaseModel, Field
import datetime as dt
from enum import Enum
from typing import List

class Brand(str, Enum):
    SWIX = "Swix"
    TOKO = "Toko"
    RODE = "Rode"


class Application(str, Enum):
    GEBUEGELT = "Gebügelt"
    GEKORKT = "Gekorkt"
    VERRIEBEN = "Verrieben"


class SingleLayer(BaseModel):
    brand: Brand = Field(default=Brand.SWIX, description="Brand of the product")
    name: str = Field(default="", description="Name of the product")
    application: Application = Field(default=Application.GEBUEGELT, description="Application of the product")

    def __str__(self):
        return f"{self.brand.value} {self.name} - {self.application.value}"


class KickWaxEntry(BaseModel):
    name: str = Field(..., description="Name of the event")
    location: str = Field(..., description="Location of the event")
    date: dt.date = Field(default=dt.date.today(), description="Date of the event")
    success_rate: int = Field(default=3, ge=1, le=5, description="Success rating")
    layers: List[SingleLayer] = Field(..., description="Wax layers applied")

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data['date'] = self.date.isoformat()
        return data