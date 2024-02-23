import pandas as pd
import streamlit as st
from pydantic_settings import BaseSettings
from requests import get, Response
from typing import Any
from urllib import parse


class WeblingConfig(BaseSettings):
    apiUrl: str = 'https://zuerichdoppelstock.webling.ch/api/1'
    apiKey: str = ''

    class Config:
        env_file = '.env'
        env_prefix = 'WEBLING_'


cfg = WeblingConfig()


def get_call(route: str, params: dict[str, Any] = {}) -> Response:
    params['apikey'] = cfg.apiKey
    return get(f'{cfg.apiUrl}/{route}', params=params)


def get_google_sheet(spreadsheet_id: str, sheet_id: str, format: str = 'csv') -> pd.DataFrame:
    url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format={format}&gid={sheet_id}'
    return pd.read_csv(url)


class VisualCrossingConfig(BaseSettings):
    apiUrl: str = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services'
    apiKey: str = ''

    class Config:
        env_file = '.env'
        env_prefix = 'VISUALCROSSING_'


vc_cfg = VisualCrossingConfig()

@st.cache_data
def load_forecast(location: str, id: int) -> pd.DataFrame:
    loc = parse.quote_plus(location)
    url = f'{vc_cfg.apiUrl}/timeline/{loc}?unitGroup=metric&include=hours&key={vc_cfg.apiKey}&contentType=csv'
    return pd.read_csv(url, delimiter=',', index_col='datetime', parse_dates=True)