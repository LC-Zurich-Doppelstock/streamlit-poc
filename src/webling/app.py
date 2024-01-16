import altair as alt
import pandas as pd
import streamlit as st
from streamlit.logger import get_logger
from members import Member, MemberGroup
from rest_calls import get_call
from datetime import date, datetime


LOGGER = get_logger(__name__)
STATE_KEY = 'load_counter'

def get_members() -> list[Member]:
    # data = get_call('membergroup', {'format': 'full'}).json()
    # groups = [MemberGroup(**group) for group in data]
    # LOGGER.info('Loaded %d groups from Webling' % len(groups))
    data = get_call('member', {'format': 'full'}).json()
    members = [Member(**member) for member in data]
    LOGGER.info('Loaded %d members from Webling' % len(members))
    return members


def run():
    LOGGER.info('Starting app')

    st.set_page_config(
        page_title='LC ZH DS',
        page_icon=':palm_tree:',
    )
    st.session_state[STATE_KEY] = 0

    st.title("LC Zürich Doppelstock Mitgliederstatistik")
    st.write("Diese App visualisiert die Mitgliederstatistik von LC Zürich Doppelstock.")
    st.write("Die Daten werden anonymisiert von Webling geladen und in der App verarbeitet.")
    st.write("Die Daten werden nicht gespeichert oder weiterverarbeitet.")

    LOGGER.info('Loading members')
    members = get_members()

    LOGGER.info('Creating chart')
    years = range(2016, date.today().year + 1)
    m_count = [len([member for member in members if member.is_active(year) and not member.talent]) for year in years]
    t_count = [len([member for member in members if member.is_active(year) and member.talent]) for year in years]
    df = pd.DataFrame({
        'Jahr': years,
        'Talenterhaltung': m_count,
        'Talentförderung': t_count
    }).melt('Jahr', var_name='Mitglieder', value_name='Summe')

    chart = alt.Chart(df).mark_bar().encode(
        x='Jahr:O',
        y='Summe:Q',
        color=alt.Color('Mitglieder', scale=alt.Scale(domain=['Talentförderung', 'Talenterhaltung'], range=['pink', 'lightgreen'])),
        tooltip=['Mitglieder', 'Summe'],
        order=alt.Order('Mitglieder', sort='ascending')
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    if st.button("re-load data"):
        members = get_members()
        st.info('Loaded %d members from Webling (%s)' % (len(members), datetime.now().strftime('%H:%M:%S')))


if __name__ == '__main__':
    run()