import os
import altair as alt
import datetime as dt
import pandas as pd
from pydantic import BaseModel
import streamlit as st
from streamlit.logger import get_logger
import yaml
from data import load_forecast
from utils import page_config


LOGGER = get_logger(__name__)
LOGGER.setLevel('DEBUG')
RESOURCES_PATH = 'src/resources/weather'
DEBUG = False

page_config()

class Checkpoint(BaseModel):
    name: str
    distance: float
    coordinates: tuple[float, float, float]

    def __hash__(self):
        return hash((self.coordinates[0], self.coordinates[1]))

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return self.__hash__() == other.__hash__()
        return NotImplemented

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

# icons: https://github.com/visualcrossing/WeatherIcons/tree/main/PNG/2nd%20Set%20-%20Color
cols = ['temp','feelslike','dew','humidity','precip','precipprob','preciptype','snow','snowdepth','windgust','windspeed','winddir','cloudcover','conditions','icon']
cols_std = ['km', 'time']
cache_file = f'{RESOURCES_PATH}/forecast.csv'
if DEBUG and os.path.exists(cache_file):
    forecast = pd.read_csv(cache_file, delimiter=',', index_col=0, parse_dates=True)
else:
    rows = []
    for checkpoint in race.checkpoints:
        cache_id = dt.datetime.now().hour
        data = load_forecast(f'{checkpoint.coordinates[0]},{checkpoint.coordinates[1]}', cache_id)[cols]
        t = race.start + dt.timedelta(hours=checkpoint.distance/race.distance*time.hour)
        i = min(data.index, key=lambda d: abs(d - t))
        row = data.loc[i]
        row['name'] = checkpoint.name
        row['km'] = checkpoint.distance
        row['time'] = t.time()
        rows.append(row)
    forecast = pd.concat(rows, axis=1).transpose()
    forecast.reset_index(inplace=True, drop=True)
    forecast.set_index('name', inplace=True)
    forecast = forecast[cols_std + cols]
    forecast.to_csv(cache_file)
    

st.write('---')

cols_selected = st.multiselect(
    'Select Columns',
    cols, default=['temp', 'feelslike', 'precip', 'windspeed', 'winddir', 'conditions'])
st.dataframe(forecast[cols_std + cols_selected])

with st.expander('temperatures (WIP)'):
    data = forecast.reset_index()[['km', 'temp', 'feelslike', 'dew']].melt('km')
    chart = alt.Chart(data).mark_line().encode(
        x=alt.X('km', axis=alt.Axis(title='Distance [km]')),
        y=alt.Y('value', axis=alt.Axis(title='Temperature [°C]')),
        color='variable'
    )
    st.altair_chart(chart, use_container_width=True)