import os
import streamlit as st
from data import get_call
from supabase import AuthApiError, AuthWeakPasswordError, Client, create_client
from typing import Callable
from webling.members import Member, Status

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def get_supabase_client() -> Client:
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    if not url or not key:
        st.error('SUPABASE_URL or SUPABASE_KEY not set')
        st.stop()
    return create_client(url, key)

supabase = get_supabase_client()

@st.cache_data(ttl=10)
def get_data(_supabase: Client, table: str) -> list[dict]:
    return _supabase.table(table).select("*").execute().data

LOGIN_STATE = "logged_in"

def set_login_state(state: bool):
    st.session_state[LOGIN_STATE] = state
    st.rerun()

def is_logged_in() -> bool:
    return st.session_state.get(LOGIN_STATE, False)
    

def validate_active_member(email: str) -> Member:
    data = get_call('member', {'format': 'full'}).json()
    members = [Member(**member) for member in data]
    member = next((member for member in members if member.email == email and member.status == Status.Aktiv), None)
    if not member:
        st.error(f"No active member found in Webling with email {email}.")
        st.stop()
    return member

def login(email: str, password: str):
    validate_active_member(email)
    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    st.success("Logged in successfully.")
    set_login_state(True)

def signup(email: str, password: str):
    validate_active_member(email)
    app_url = os.getenv("APP_URL")
    if not app_url:
        st.error("APP_URL not set")
        st.stop()
    body = {
        "email": email,
        "password": password,
        "options": {
            "email_redirect_to": app_url + "/Supabase"
        }
    }
    response = supabase.auth.sign_up(body)
    if len(response.user.identities) > 0:
        st.success("User created successfully. Please check your email for a verification link.")
    else:
        st.warning("User already exists. Please log in.")

def handle_action(clicked: bool, func: Callable[[], None]):
    if clicked:
        try:
            func()
        except (AuthWeakPasswordError, AuthApiError) as e:
            st.error(e)
            st.stop()

def init():
    tab1, tab2 = st.tabs(["Log In", "Register"])
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", help="Your e-mail address listed in Webling")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Log In", type="primary")
            handle_action(submit, lambda: login(email, password))
    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email", help="Your e-mail address listed in Webling")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Register", type="primary")
            handle_action(submit, lambda: signup(email, password))

# Main
if not is_logged_in():
    st.write("You are not logged in. Please log in or sign up.")
    init()
else:
    user = supabase.auth.get_user()
    if not user:
        st.error("No User logged in.")
        st.stop()
    member = validate_active_member(user.user.email)
    if not member:
        st.error("No active member found in Webling with email {user.user.email}.")
        st.stop()
    st.markdown(f"Welcome *:blue[{member.first_name} {member.last_name}]*")

    st.table(get_data(supabase, "test"))
