import hmac
import pandas as pd
import streamlit as st
from streamlit.logger import get_logger
from data import get_call
from utils import page_config
from webling.material import Article


LOGGER = get_logger(__name__)

page_config()


def check_password():
    """Returns `True` if the user had the correct password."""
    pwd_key = 'interna_password'
    ok_key = 'password_ok'
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state[pwd_key], st.secrets[pwd_key]):
            st.session_state[ok_key] = True
            del st.session_state[pwd_key]  # Don't store the password.
        else:
            st.session_state[ok_key] = False

    # Return True if the password is validated.
    if st.session_state.get(ok_key, False):
        return True

    # Show input for password.
    st.text_input(
        'Passwort', type='password', on_change=password_entered, key=pwd_key
    )
    if ok_key in st.session_state:
        st.error('😕 Password incorrect')
    return False


def get_material() -> list[Article]:
    data = get_call('article', {'format': 'full'}).json()
    articles = [Article(**article) for article in data]
    LOGGER.info('Loaded %d articles from Webling' % len(articles))
    return articles


if not check_password():
    st.stop()  # Do not continue if check_password is not True.


st.title("Materialverwaltung")
material = get_material()
df = pd.DataFrame([(m.title, m.price, m.quantity) for m in material], columns=['Material', 'Preis', 'Anzahl'])
st.table(df)
st.write('momentaner Materialwert:', sum(m.price * m.quantity for m in get_material()))