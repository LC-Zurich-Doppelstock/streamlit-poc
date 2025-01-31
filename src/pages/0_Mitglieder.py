from datetime import date, datetime
import json
import pandas as pd
import pathlib
import plotly.express as px
import streamlit as st
from streamlit.logger import get_logger

from data import get_call
from models.year_stats import YearStats
from utils import page_config
from webling.members import Member


LOGGER = get_logger(__name__)

def get_members() -> list[Member]:
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


# PLOT NUMBER OF ACTIVE MEMBERS
m_count = [len([member for member in members if member.is_active(year) and not member.talent]) for year in years]
t_count = [len([member for member in members if member.is_active(year) and member.talent]) for year in years]

cat_bar_plot('Anzahl Mitglieder im Verlauf der Zeit', 'Jahr', years, 'Anzahl', 'Mitglieder',
         ['Talenterhaltung', 'Talentförderung'], [m_count, t_count], ['lightgrey', 'grey'])

# PLOT MEMBERSHIP CHANGES PER YEAR 
n_count = [len([member for member in members if member.joined(year)]) for year in years]
a_count = [len([member for member in members if member.left(year)]) for year in years]

cat_bar_plot('Anzahl Neuzugänge und -abgänge pro Jahr', 'Jahr', years, 'Anzahl', 'Ereignis',
         ['Eintritte', 'Austritte'], [n_count, a_count], ['lightgreen', 'orange'])

# Create pivot table data
heart_rate_data = []
for year in years:
    rates = [member.heart_rate for member in members if member.is_active(year) and member.heart_rate != 0]
    for rate in rates:
        heart_rate_data.append({'year': year, 'heart_rate': rate})
heart_rates = pd.DataFrame(heart_rate_data)

# PLOT HEART RATE DISTRIBUTION PER YEAR
fig = px.box(heart_rates, y='heart_rate', x='year')
fig.update_layout(
    title='Verteilung der Ruhepulse pro Jahr',
    yaxis_title='Ruhepuls',
    xaxis_title='Jahr'
)
st.plotly_chart(fig, use_container_width=True)

# dump year stats
year_stats = []
for year, m_count, t_count, n_count, a_count in zip(years, m_count, t_count, n_count, a_count):
    rates = heart_rates[heart_rates['year'] == year]['heart_rate']
    rates = [int(rate) for rate in rates]
    year_stats.append(
        YearStats(
            year=year,
            active_members=m_count,
            talent_members=t_count,
            new_members=n_count,
            left_members=a_count,
            heart_rates=rates))
# Write year stats to JSON file
history_file = pathlib.Path(__file__).resolve().parent.parent / 'resources' / 'year_stats.json'
with open(history_file, 'w') as f:
    json_data = [stat.model_dump() for stat in year_stats]
    json.dump(json_data, f, indent=2)


if st.button("re-load data"):
    members = get_members()
    st.info('Loaded %d members from Webling (%s)' % (len(members), datetime.now().strftime('%H:%M:%S')))
