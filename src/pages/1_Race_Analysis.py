import pandas as pd
import streamlit as st
import altair as alt
from utils import page_config
from data import get_google_sheet
from plot_config import CONFIGS
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
    st.stop()
filtered_df = df_raw.loc[selected_skiers]

# select a plot type and pre-process the data
plot_type = st.sidebar.selectbox('Select a plot type', CONFIGS)
if plot_type is None:
    st.stop()
df = plot_type.pre_process(filtered_df)

# Reshape the dataframe to long format
df_melt = df.reset_index().melt(id_vars='skier', var_name='km', value_name='time')
# and convert the km column to numeric
df_melt['km'] = pd.to_numeric(df_melt['km'])

# Create a new line plot for the selected skiers
chart = alt.Chart(df_melt).mark_line().encode(
    x=alt.X('km', title='Race Distance [km]', sort=[int(i) for i in df.columns]),
    y=alt.Y('time', title=plot_type.y_label),
    color='skier'
).interactive()

# Display the line plot for the selected skiers
st.altair_chart(chart, use_container_width=True)