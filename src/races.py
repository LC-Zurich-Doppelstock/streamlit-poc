import datetime as dt
from pydantic import BaseModel
import yaml


class Race(BaseModel):

    name: str
    date: dt.date
    location: str
    distance: int
    url: str
    doc_id: str
    sheet_id: str
    seedings: dict[str, dict[str, dt.timedelta]] = {}

    def __str__(self) -> str:
        return self.name

RACES = []
with open('src/resources/races.yml', 'r') as stream:
    try:
        races = yaml.safe_load(stream)
        RACES = [Race(**race) for race in races]
    except yaml.YAMLError as e:
        print(e)