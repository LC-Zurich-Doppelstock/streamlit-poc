import streamlit as st
import altair as alt
from google_sheets import get_sheet
from utils import page_config

page_config()

df_raw = get_sheet('1yKpap4SXwDw6r8-JPViEgNwJw_a-POd13Y47790tGwo', 0)

# Reshape the dataframe to long format
df = df_raw.melt(id_vars='skier', var_name='km', value_name='time')

# Add a dropdown to select skiers
skiers = df['skier'].unique()
selected_skiers = st.multiselect('Select skiers', skiers)

# Filter the dataframe based on the selected skiers

filtered_df = df[df['skier'].isin(selected_skiers)]

# Create a new line plot for the selected skiers
filtered_chart = alt.Chart(filtered_df).mark_line().encode(
    x='km:Q',
    y='time',
    color='skier'
).interactive()

# Display the line plot for the selected skiers
st.altair_chart(filtered_chart, use_container_width=True)

