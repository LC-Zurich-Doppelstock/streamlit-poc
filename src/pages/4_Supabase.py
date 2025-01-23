import streamlit as st
import streamlit_react_jsonschema as srj
import pandas as pd

from data import get_active_member, LoginHandler
from models.kick_wax import KickWaxEntry, KickWaxAdd
from pydantic import ValidationError


if "login_handler" not in st.session_state:
    st.session_state["login_handler"] = LoginHandler()
login_handler = st.session_state["login_handler"]

def init():
    # initial login state
    login_handler.set_authorized_user()
    # if not logged in, show login form
    if not login_handler.is_logged_in():
        with st.sidebar.expander("You are not logged in. Please log in or register."):
            with st.form("login_form"):
                email = st.text_input("Email", help="Your e-mail address listed in Webling")
                password = st.text_input("Password", type="password")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Log In", type="primary"):
                        login_handler.login(email, password)
                with col2:
                    if st.form_submit_button("Register", type="secondary", help="Register a new user"):
                        login_handler.signup(email, password)
                # TODO: Add a button to reset password
                st.stop()
    # otherwise show the user info
    else:
        with st.sidebar.expander("You are logged in."):
            user = login_handler.get_authorized_user()
            if not user:
                st.error("No User logged in.")
                st.stop()
            member = get_active_member(user.email)
            if not member:
                st.error("No active member found in Webling with email {user.user.email}.")
                st.stop()
            st.markdown(f"Welcome *:blue[{member.first_name} {member.last_name}]*")

# Main
init()
supabase = login_handler.supabase_client

# load data
data = pd.DataFrame(supabase.table("kickwax").select("*").execute().data)
data["mine"] = data["created_by"] == login_handler.get_authorized_user().id

# Select only relevant columns for display
display_columns = ["date", "name", "location", "success_rate", "mine"]
summary = data[display_columns]
# display table
table = st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True,
    column_order=display_columns,
    on_select="rerun",
    selection_mode="single-row")

# view/edit/delete
if not table.selection.rows:
    st.info("Select a row from the table.")
else:
    selected_index = table.selection.rows[0]
    entry = KickWaxEntry(**data.iloc[selected_index])
        
    # view
    st.subheader(f"Wax layers for {entry.name} on {entry.date}")
    for layer in entry.layers:
        st.write(str(layer))
    
    # only allow deletion of own entries
    if entry.mine:
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