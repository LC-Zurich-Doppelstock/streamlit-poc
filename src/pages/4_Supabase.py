import os
import streamlit as st
from data import get_active_member, get_supabase_client
from supabase import AuthApiError, AuthWeakPasswordError
from models.kick_wax import KickWaxEntry, KickWaxAdd
from typing import Callable
from pydantic import ValidationError
import streamlit_react_jsonschema as srj


supabase = get_supabase_client()

LOGIN_STATE = "logged_in"

def set_login_state(state: bool):
    st.session_state[LOGIN_STATE] = state

def is_logged_in() -> bool:
    return st.session_state.get(LOGIN_STATE, False)    

def login(email: str, password: str):
    member = get_active_member(email)
    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    st.success("Logged in successfully.")
    set_login_state(True)
    st.rerun()

def signup(email: str, password: str):
    member = get_active_member(email)
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
    # initial login state
    set_login_state(supabase.auth.get_user() is not None)
    # if not logged in, show login form
    if not is_logged_in():
        with st.sidebar.expander("You are not logged in. Please log in or register."):
            with st.form("login_form"):
                email = st.text_input("Email", help="Your e-mail address listed in Webling")
                password = st.text_input("Password", type="password")
                col1, col2 = st.columns(2)
                with col1:
                    login_button = st.form_submit_button("Log In", type="primary")
                with col2:
                    signup_button = st.form_submit_button("Register", type="secondary", help="Register a new user")
                # TODO: Add a button to reset password
                handle_action(login_button, lambda: login(email, password))
                handle_action(signup_button, lambda: signup(email, password))
    # otherwise show the user info
    else:
        with st.sidebar.expander("You are logged in."):
            user = supabase.auth.get_user()
            if not user:
                st.error("No User logged in.")
                st.stop()
            member = get_active_member(user.user.email)
            if not member:
                st.error("No active member found in Webling with email {user.user.email}.")
                st.stop()
            st.markdown(f"Welcome *:blue[{member.first_name} {member.last_name}]*")

# Main
init()
if not is_logged_in():
    st.stop()

# load data
data = supabase.table("kickwax").select("*").execute().data

# Select only relevant columns for display
user_id = supabase.auth.get_user().user.id
display_columns = ['date', 'name', 'location', 'success_rate']
summary = [
    {
        **{k: v for k, v in entry.items() if k in display_columns},
        **{'mine': entry.get('created_by') == user_id}
    } for entry in data
]
display_columns.append('mine')
table = st.dataframe(summary, use_container_width=True, hide_index=True, column_order=display_columns, on_select="rerun", selection_mode="single-row")

# view/edit/delete
if not table.selection.rows:
    st.info("Select a row from the table.")
else:
    selected_index = table.selection.rows[0]
    entry = KickWaxEntry(**data[selected_index])
        
    # view
    st.subheader(f"Wax layers for {entry.name} on {entry.date}")
    for layer in entry.layers:
        st.write(str(layer))
    
    # delete
    with st.expander(f"Delete {entry}"):
        if st.button("Yes, delete", key="confirm_delete", type="primary"):
            supabase.table("kickwax").delete().eq("id", entry.id).execute()
            st.success("Deleted entry.")
            st.rerun()
        if st.button("No, cancel", key="cancel_delete", type="secondary"):
            st.rerun()

# add new entry
with st.expander("Add new entry"):
    value, submitted = srj.pydantic_form(model=KickWaxAdd)   
    if submitted and value:
        try:
            obj = KickWaxAdd.model_validate(value)
            supabase.table("kickwax").insert(obj.model_dump()).execute()
            st.success(f"Added new entry {obj}")
        except ValidationError as e:
            st.error(e)