import streamlit as st
import pandas as pd
import plotly.express as px
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

def cat_bar_plot(title: str, x_label: str, x_values: list, y_label: str, category: str,
             cat_labels: list[str], cat_values: list[list], cat_colors: list[str]):
    data = {x_label: x_values}
    data.update({k: v for k,v in zip(cat_labels, cat_values)})
    df = pd.DataFrame(data).melt(x_label, var_name=category, value_name=y_label)
    fig = px.bar(
        df, x=x_label, y=y_label, color=category,
        title=title,
        barmode='group',
        color_discrete_map={cat: color for cat, color in zip(cat_labels, cat_colors)},
        category_orders={category: cat_labels})
    fig.update_layout(xaxis={'type': 'category'}, legend_title=category)
    st.plotly_chart(fig, use_container_width=True)


page_config()

st.title("Vereinsmitglieder Statistik")
st.write("Die Daten werden anonymisiert von Webling geladen und in der App verarbeitet.")
st.write("Die Daten werden nicht gespeichert oder weiterverarbeitet.")

LOGGER.info('Loading members')
members = get_members()

LOGGER.info('Creating charts')
years = list(range(2016, date.today().year + 1))

# Anzahl Mitglieder pro Jahr
m_count = [len([member for member in members if member.is_active(year) and not member.talent]) for year in years]
t_count = [len([member for member in members if member.is_active(year) and member.talent]) for year in years]

cat_bar_plot('Anzahl Mitglieder im Verlauf der Zeit', 'Jahr', years, 'Anzahl', 'Mitglieder',
         ['Talenterhaltung', 'Talentförderung'], [m_count, t_count], ['green', 'blue'])

# Anzahl Neuzugänge und -abgänge pro Jahr
n_count = [len([member for member in members if member.joined(year)]) for year in years]
a_count = [len([member for member in members if member.left(year)]) for year in years]

cat_bar_plot('Anzahl Neuzugänge und -abgänge pro Jahr', 'Jahr', years, 'Anzahl', 'Ereignis',
         ['Neuzugänge', 'Austritte'], [n_count, a_count], ['lightgreen', 'orange'])


if st.button("re-load data"):
    members = get_members()
    st.info('Loaded %d members from Webling (%s)' % (len(members), datetime.now().strftime('%H:%M:%S')))