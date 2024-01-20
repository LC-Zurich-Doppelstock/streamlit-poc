import streamlit as st
from google_sheets import get_sheet
from utils import page_config


page_config()

df3 = get_sheet('1yKpap4SXwDw6r8-JPViEgNwJw_a-POd13Y47790tGwo', 0)
st.dataframe(df3)