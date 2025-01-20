import streamlit as st
from supabase import create_client, Client, AuthInvalidCredentialsError
import os
from webling.members import Member, Status
from data import get_call

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

LOGIN_STATE = "logged_in"

def set_login_state(state: bool):
    st.session_state[LOGIN_STATE] = state
    st.rerun()

def is_logged_in() -> bool:
    return st.session_state.get(LOGIN_STATE, False)

def get_active_member(email: str) -> Member | None:
    data = get_call('member', {'format': 'full'}).json()
    members = [Member(**member) for member in data]
    return next((member for member in members if member.email == email and member.status == Status.Aktiv), None)

def login():
    if not is_logged_in():
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Log In")
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Log In")
                if submit:
                    try:
                        supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        set_login_state(True)
                        st.rerun()
                    except Exception:
                        st.error("Invalid email or password")
                        st.stop()

        with col2:
            st.subheader("Register")
            with st.form("signup_form"):
                email = st.text_input("Email (your e-mail address listed in Webling)")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Register")
                if submit:
                    if not get_active_member(email):
                        st.error(f"No active member found in Webling with email {email}.")
                        st.stop()
                    body = {
                        "email": email,
                        "password": password,
                        "options": {
                            "email_redirect_to": os.getenv("HOST", "http://localhost:8501") + "/supabase"
                        }
                    }
                    try:
                        supabase.auth.sign_up(body)
                    except Exception as e:
                        st.error(f"Something went wrong while registering: {e}")
                        st.stop()
                    

if not is_logged_in():
    st.write("You are not logged in. Please log in or sign up.")
    login()
else:
    user = supabase.auth.get_user()
    if not user:
        st.error("User not found")
        st.stop()
    member = get_active_member(user.user.email)
    if not member:
        st.stop()
    st.markdown(f"Welcome *:blue[{member.first_name} {member.last_name}]*")

    st.table(supabase.table("test").select("*").execute().data)
