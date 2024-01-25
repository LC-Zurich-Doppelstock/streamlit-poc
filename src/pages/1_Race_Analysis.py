import pandas as pd
import streamlit as st
from utils import page_config
from data import get_google_sheet
from race_plots import RACE_PLOTS, add_seedings
from races import RACES
from streamlit.logger import get_logger


LOGGER = get_logger(__name__)

page_config()
st.sidebar.title('Configuaration')

# race selection
race = st.sidebar.selectbox('Select a race', RACES)
if race is None:
    st.write('Please select a race first')
    st.stop()
st.title(race.name)
st.write(f'{race.location}, {race.date.strftime("%d.%m.%Y")}, {race.url}, {race.distance} km')
st.write('---')

# load data
df_raw = get_google_sheet(race.doc_id, race.sheet_id)
df_raw = df_raw.set_index('skier')
df_raw = df_raw.apply(pd.to_datetime, format='%H:%M:%S')

# add average skier for each seeding time
df_seed = add_seedings(df_raw, race.seedings)

# skiers selection
selected_skiers = st.sidebar.multiselect('Select skiers', df_seed.index)
if selected_skiers == []:
    st.write('Please select skiers')
    st.stop()
filtered_df = df_seed.loc[selected_skiers]

# select a plot type and pre-process the data
plot = st.sidebar.selectbox('Select a plot type', RACE_PLOTS)
if plot is None:
    st.stop()

# Display the line plot for the selected skiers
fig = plot.make_figure(filtered_df)
st.write(plot.explanation)
st.plotly_chart(fig, use_container_width=True)