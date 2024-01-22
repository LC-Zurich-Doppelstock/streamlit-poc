import streamlit as st
from streamlit.logger import get_logger
from utils import page_config


LOGGER = get_logger(__name__)


def run():
    page_config()
    st.title("LC Zürich-Doppelstock Data Analysis")

    st.write("Diese App visualisiert diverse Daten von/für/durch Langlaufclub Zürich-Doppelstock.")


if __name__ == '__main__':
    LOGGER.info('Starting app')
    run()