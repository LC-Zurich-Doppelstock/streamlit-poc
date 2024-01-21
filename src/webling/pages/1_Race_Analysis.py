from enum import Enum
import pandas as pd
import streamlit as st
import altair as alt
from google_sheets import get_sheet
from utils import page_config


page_config()

# available races
races = {
    'La Diagonela 2024': 0
}

# race selection
race = st.selectbox('Select a race', races.keys())
if race is None:
    st.stop()
df_raw = get_sheet('1yKpap4SXwDw6r8-JPViEgNwJw_a-POd13Y47790tGwo', races[race])
df_raw = df_raw.set_index('skier')
df_raw = df_raw.apply(pd.to_datetime)

# skiers selection
selected_skiers = st.multiselect('Select skiers', df_raw.index)
filtered_df = df_raw.loc[selected_skiers]


# plot type selection
class PlotType(str, Enum):
    TIME = 'Race Time'
    DIFF_FASTEST = 'Time difference to fastest from selection'

plot_type = st.selectbox('Select a plot type', [e.value for e in PlotType])
if plot_type is None:
    st.stop()

match plot_type:
    case PlotType.DIFF_FASTEST:
        # find column with end time
        km = [int(i) for i in df_raw.columns]
        # find fastest skier
        fastest_skier = filtered_df[str(max(km))].idxmin()
        # calculate difference to fastest skier
        df = filtered_df.sub(filtered_df.loc[fastest_skier])
    case _:
        df = filtered_df

# Reshape the dataframe to long format
df_melt = df.reset_index().melt(id_vars='skier', var_name='km', value_name='time')

# Create a new line plot for the selected skiers
chart = alt.Chart(df_melt).mark_line().encode(
    x='km:Q',
    y='time',
    color='skier'
).interactive()

# Display the line plot for the selected skiers
st.altair_chart(chart, use_container_width=True)