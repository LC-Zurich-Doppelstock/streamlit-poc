from typing import Callable
import pandas as pd
from pydantic_settings import BaseSettings


class PlotConfig(BaseSettings):
    name: str
    y_label: str
    pre_process: Callable[[pd.DataFrame], pd.DataFrame] = lambda df: df

    def __str__(self) -> str:
        return self.name


def make_diff_to_fastest(data: pd.DataFrame) -> pd.DataFrame:
    km = [int(i) for i in data.columns]
    # find column with end time
    end_time = str(max(km))
    # find fastest skier
    fastest_skier = data[end_time].idxmin()
    # calculate difference to fastest skier, assuming to have started at the same time
    df = data.sub(data.loc[fastest_skier])
    df = df.apply(pd.to_numeric)/(60*1e9)
    df = df.sub(df.loc[:,str(min(km))], axis=0)
    return df


CONFIGS = [
    PlotConfig(
        name='Race Time',
        y_label='Time [HH:MM:SS]'),
    PlotConfig(
        name='Time difference to fastest from selection',
        y_label='Time difference [min]',
        pre_process=make_diff_to_fastest)
]