from typing import Callable
import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure
from pydantic_settings import BaseSettings


class RacePlot(BaseSettings):

    name: str
    explanation: str
    y_label: str
    pre_process: Callable[[pd.DataFrame], pd.DataFrame] = lambda df: df

    def __str__(self) -> str:
        return self.name
    
    def make_figure(self, data: pd.DataFrame) -> Figure:
        df = self.pre_process(data)
        # Convert the dataframe to long format
        df_long = df.reset_index().melt(id_vars='skier', var_name='km', value_name='time')
        # Convert the km column to numeric
        df_long['km'] = pd.to_numeric(df_long['km'])
        fig = px.line(
            df_long, x='km', y='time', color='skier',
            title=self.name,
            labels={
                'km': 'Race Distance [km]',
                'time': self.y_label
            })
        return fig


def make_diff_to_winner(data: pd.DataFrame) -> pd.DataFrame:
    km = [int(i) for i in data.columns]
    # find column with end time
    end_time = str(max(km))
    # find fastest skier
    fastest_skier = data[end_time].idxmin()
    # calculate difference to fastest skier, assuming to have started at the same time
    df = data.sub(data.loc[fastest_skier])*(-1)
    df = df.apply(pd.to_numeric)/(60*1e9)
    df = df.sub(df.loc[:,str(min(km))], axis=0)
    return df


def make_diff_to_winner_section(data: pd.DataFrame) -> pd.DataFrame:
    df = make_diff_to_winner(data)
    df = df.diff(axis=1)
    km = [int(i) for i in data.columns]
    df = df * 60 / km
    df.fillna(0, inplace=True)
    return df

    
def make_diff_to_leader(data: pd.DataFrame) -> pd.DataFrame:
    km = [int(i) for i in data.columns]
    # find fastest time per section
    min_times = data.min()
    # calculate difference to fastest skier, assuming to have started at the same time
    df = data.sub(min_times)
    df = df.apply(pd.to_numeric)/(60*1e9)
    df = df.sub(df.loc[:,str(min(km))], axis=0)*(-1)
    return df


RACE_PLOTS = [
    RacePlot(
        name='vs. leader of selection',
        explanation='Time gap to the leader of the race at the specific checkpoint, considering only the selected skiers.',
        y_label='Time difference [min]',
        pre_process=make_diff_to_leader),
    RacePlot(
        name='vs. winner of selection',
        explanation='Time difference to the eventual winner of the race, considering only the selected skiers.',
        y_label='Time difference [min]',
        pre_process=make_diff_to_winner),
    RacePlot(
        name='Race Time',
        explanation='The official race time of the selected skiers.',
        y_label='Time [HH:MM:SS]'),
    RacePlot(
        name='sec/km vs. winner from selection, ',
        explanation='Speed difference between checkpoints against eventual winner, considering only the selected skiers.',
        y_label='Speed difference [sec/km]',
        pre_process=make_diff_to_winner_section)
]