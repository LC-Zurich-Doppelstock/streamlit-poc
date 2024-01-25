import pandas as pd
from pydantic_settings import BaseSettings
from requests import get, Response
from typing import Any


class ApiConfig(BaseSettings):
    apiUrl: str = 'https://zuerichdoppelstock.webling.ch/api/1'
    apiKey: str = ''

    class Config:
        env_file = '.env'
        env_prefix = 'WEBLING_'


cfg = ApiConfig()


def get_call(route: str, params: dict[str, Any] = {}) -> Response:
    params['apikey'] = cfg.apiKey
    return get(f'{cfg.apiUrl}/{route}', params=params)


def get_google_sheet(spreadsheet_id: str, sheet_id: str, format: str = 'csv') -> pd.DataFrame:
    url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format={format}&gid={sheet_id}'
    return pd.read_csv(url)