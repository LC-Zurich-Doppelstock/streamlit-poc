import datetime as dt
import pandas as pd
from pydantic import BaseModel
import streamlit as st
from streamlit.logger import get_logger
import urllib.parse
import yaml
from utils import page_config


LOGGER = get_logger(__name__)
LOGGER.setLevel('DEBUG')
RESOURCES_PATH = 'src/resources/weather'

cfg = page_config()

class Checkpoint(BaseModel):
    name: str
    distance: float
    coordinates: tuple[float, float, float]

class Race(BaseModel):
    name: str
    start: dt.datetime
    distance: float
    checkpoints: list[Checkpoint]

    def __str__(self):
        return self.name
    

with open(f'{RESOURCES_PATH}/races.yaml', 'r') as stream:
    try:
        races = yaml.safe_load(stream)
        RACES = [Race(**r) for r in races]
    except yaml.YAMLError as e:
        print(e)

race = st.selectbox('Select your race', RACES, index=0)
if not race:
    st.stop()
time = st.time_input('Select your expected race time', dt.time(6, 0))

st.write(f'{race}: {race.start}')

apiKey = 'BGD8LBFE9CN7D75ZUJ2UGKSTV'
cols = ['datetime', 'name', 'temp', 'feelslike', 'humidity','precip','precipprob','preciptype','snow','snowdepth','windgust','windspeed','winddir','cloudcover','conditions', 'icon']
# icons: https://github.com/visualcrossing/WeatherIcons/tree/main/PNG/2nd%20Set%20-%20Color
rows = []
for checkpoint in race.checkpoints:
    filename = f'{RESOURCES_PATH}/{race.name}_{checkpoint.distance:.0f}.csv'
    if False:
        location = urllib.parse.quote_plus(f'{checkpoint.coordinates[0]},{checkpoint.coordinates[1]}')
        url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}?unitGroup=metric&include=hours&key={apiKey}&contentType=csv'
        data = pd.read_csv(url, delimiter=',', index_col='datetime', parse_dates=True)
        data.to_csv(filename)
    else:
        data = pd.read_csv(filename, delimiter=',', index_col='datetime', parse_dates=True, usecols=cols, )
    
    t = race.start + dt.timedelta(hours=checkpoint.distance/race.distance*time.hour)
    i = min(data.index, key=lambda d: abs(d - t))
    row = data.loc[i]
    row['name'] = checkpoint.name
    row['km'] = checkpoint.distance
    rows.append(row)

forecast = pd.concat(rows, axis=1).transpose()
st.dataframe(forecast)