import altair as alt
import pandas as pd
import streamlit as st
from streamlit.logger import get_logger
from members import Member
from data import get_call
from datetime import date, datetime
from utils import page_config


LOGGER = get_logger(__name__)

def get_members() -> list[Member]:
    # data = get_call('membergroup', {'format': 'full'}).json()
    # groups = [MemberGroup(**group) for group in data]
    # LOGGER.info('Loaded %d groups from Webling' % len(groups))
    data = get_call('member', {'format': 'full'}).json()
    members = [Member(**member) for member in data]
    LOGGER.info('Loaded %d members from Webling' % len(members))
    return members


page_config()

st.title("Vereinsmitglieder Statistik")
st.write("Die Daten werden anonymisiert von Webling geladen und in der App verarbeitet.")
st.write("Die Daten werden nicht gespeichert oder weiterverarbeitet.")

LOGGER.info('Loading members')
members = get_members()

LOGGER.info('Creating charts')
years = range(2016, date.today().year + 1)


# PLOT NUMBER OF ACTIVE MEMBERS
st.subheader("Anzahl Mitglieder im Verlauf der Zeit")
m_count = [len([member for member in members if member.is_active(year) and not member.talent]) for year in years]
t_count = [len([member for member in members if member.is_active(year) and member.talent]) for year in years]
df1 = pd.DataFrame({
    'Jahr': years,
    'Talenterhaltung': m_count,
    'Talentförderung': t_count
}).melt('Jahr', var_name='Mitglieder', value_name='Anzahl')

chart = alt.Chart(df1).mark_bar().encode(
    x='Jahr:O',
    y='Anzahl:Q',
    color=alt.Color('Mitglieder', scale=alt.Scale(domain=['Talentförderung', 'Talenterhaltung'], range=['grey', 'lightgrey'])),
    tooltip=['Mitglieder', 'Anzahl'],
    order=alt.Order('Mitglieder', sort='ascending')
).interactive()

st.altair_chart(chart, use_container_width=True)


# PLOT MEMBERSHIP CHANGES PER YEAR 
st.subheader("Anzahl Neuzugänge und -abgänge pro Jahr")
n_count = [len([member for member in members if member.joined(year)]) for year in years]
a_count = [len([member for member in members if member.left(year)]) for year in years]
eff_count = [n_count[i] - a_count[i] for i in range(len(years))]
df2 = pd.DataFrame({
    'Jahr': years,
    'Eintritte': n_count,
    'Abgänge': a_count
}).melt('Jahr', var_name='Ereignis', value_name='Anzahl')

chart2 = alt.Chart(df2).mark_bar().encode(
    x='Jahr:O',
    y='Anzahl:Q',
    color=alt.Color('Ereignis', scale=alt.Scale(domain=['Eintritte', 'Abgänge'], range=['lightgreen', 'orange'])),
    xOffset='Ereignis',
    tooltip=['Ereignis', 'Anzahl'],
    order=alt.Order('Ereignis', sort='descending')
).interactive()

st.altair_chart(chart2, use_container_width=True)

if st.button("re-load data"):
    members = get_members()
    st.info('Loaded %d members from Webling (%s)' % (len(members), datetime.now().strftime('%H:%M:%S')))