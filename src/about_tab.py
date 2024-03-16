import datetime
import streamlit as st


def write_about_tab(latest_file_datetime: datetime.datetime, latest_match: datetime.datetime):
    st.header('About')
    st.subheader('Data retrieval')
    st.write(f'Latest data downloaded: {latest_file_datetime.replace(tzinfo=None)}')
    st.write(f'Latest recorded match: {latest_match.replace(tzinfo=None)}')
    st.subheader('Data processing')
    st.write("Player counts are recorded at the end of each match and do not account for the number of players present"
             " during the match.")
