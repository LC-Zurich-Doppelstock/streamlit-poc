import pandas as pd
import streamlit as st
from utils import page_config
from data import get_google_sheet
from race_plots import RACE_PLOTS
from streamlit.logger import get_logger


LOGGER = get_logger(__name__)

page_config()
st.sidebar.title('Configuaration')

# available races
races = {
    'La Diagonela 2024': 0
}

# race selection
race = st.sidebar.selectbox('Select a race', races.keys())
if race is None:
    st.stop()
df_raw = get_google_sheet('1yKpap4SXwDw6r8-JPViEgNwJw_a-POd13Y47790tGwo', races[race])
df_raw = df_raw.set_index('skier')
df_raw = df_raw.apply(pd.to_datetime, format='%H:%M:%S')

# skiers selection
selected_skiers = st.sidebar.multiselect('Select skiers', df_raw.index)
if selected_skiers == []:
    st.write('Please select skiers')
    st.stop()
filtered_df = df_raw.loc[selected_skiers]

# select a plot type and pre-process the data
plot = st.sidebar.selectbox('Select a plot type', RACE_PLOTS)
if plot is None:
    st.stop()

# Display the line plot for the selected skiers
fig = plot.make_figure(filtered_df)
st.write(plot.explanation)
st.plotly_chart(fig, use_container_width=True)