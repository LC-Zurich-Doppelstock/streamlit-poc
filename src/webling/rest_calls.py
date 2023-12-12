from pydantic_settings import BaseSettings
from requests import get, Response
from typing import Any


class ApiConfig(BaseSettings):
    apiUrl: str = 'https://zuerichdoppelstock.webling.ch/api/1'
    apiKey: str

    class Config:
        env_file = '.env'
        env_prefix = 'WEBLING_'


cfg = ApiConfig()


def get_call(route: str, params: dict[str, Any] = {}) -> Response:
    params['apikey'] = cfg.apiKey
    return get(f'{cfg.apiUrl}/{route}', params=params)