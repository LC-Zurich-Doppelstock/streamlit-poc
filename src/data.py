import pandas as pd
import streamlit as st
import os
from pydantic_settings import BaseSettings
from requests import get, Response
from typing import Any
from urllib import parse
from webling.members import Member, Status
from supabase import create_client, Client, AuthApiError, AuthWeakPasswordError
from gotrue.types import User, SignUpWithEmailAndPasswordCredentials
from typing import Callable


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

@st.cache_data
def get_active_member(email: str) -> Member:
    data = get_call('member', {'format': 'full'}).json()
    members = [Member(**member) for member in data]
    member = next((member for member in members if member.email == email and member.status == Status.Aktiv), None)
    if not member:
        st.error(f"No active member found in Webling with email {email}.")
        st.stop()
    return member

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


class SupaBaseConfig(BaseSettings):
    url: str = ''
    key: str = ''
    email: str = ''
    password: str = ''

    class Config:
        env_file = '.env'
        env_prefix = 'SUPABASE_'

supabase_cfg = SupaBaseConfig()

class LoginHandler:
    supabase_client: Client
    authorized_user: User | None

    def __init__(self):
        if not supabase_cfg.url or not supabase_cfg.key:
            st.error('SUPABASE_URL or SUPABASE_KEY not set')
            st.stop()
        self.supabase_client = create_client(supabase_cfg.url, supabase_cfg.key)
        try:
            self.supabase_client.auth.sign_in_with_password({
                "email": supabase_cfg.email,
                "password": supabase_cfg.password
            })
        except Exception:
            pass

    def set_authorized_user(self):
        user_response = self.supabase_client.auth.get_user()
        self.authorized_user = user_response.user if user_response else None

    def get_authorized_user(self) -> User | None:
        return self.authorized_user

    def is_logged_in(self) -> bool:
        return self.authorized_user is not None
    
    def login(self, email: str, password: str):
        def login_func():
            member = get_active_member(email)
            response = self.supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            st.success("Logged in successfully.")
            self.set_authorized_user()
            st.rerun()
        self._handle_action(login_func)
    
    def signup(self, email: str, password: str):
        def signup_func():
            member = get_active_member(email)
            app_url = os.getenv("APP_URL")
            if not app_url:
                st.error("APP_URL not set")
                st.stop()
            body = SignUpWithEmailAndPasswordCredentials(
                email=email,
                password=password,
                options={
                    "email_redirect_to": app_url + "/Supabase"
                }
            )
            response = self.supabase_client.auth.sign_up(body)
            if response.user and response.user.identities and len(response.user.identities) > 0:
                st.success("User created successfully. Please check your email for a verification link.")
            else:
                st.warning("User already exists. Please log in.")
        self._handle_action(signup_func)
    
    def _handle_action(self, func: Callable[[], None]):
        try:
            func()
        except (AuthWeakPasswordError, AuthApiError) as e:
            st.error(e)
            st.stop()
