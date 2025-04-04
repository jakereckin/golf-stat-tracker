import streamlit as st
import polars as pl
import pandas as pd
import sqlitecloud
from py import sql

st.header(body='Add Clubs', divider='blue')
sql_lite_connect = st.secrets['sqlite_connection']['GOLF_CONNECTION']

club_name = st.text_input(label='Club')
club_type = st.selectbox(
    label='Club Type',
    options=['Driver', 'Wood', 'Iron', 'Wedge', 'Putter']
)
club_brand = st.text_input(label='Brand')
active = st.checkbox(label='Active', value=True)

add_club = st.button(label='Add Club')
if add_club:
    with sqlitecloud.connect(sql_lite_connect) as conn:
        if active:
            active = 1
        else:
            active = 0
        cursor = conn.cursor()
        cursor.execute(
            sql=sql.insert_club_sql(),
            parameters=(
                club_name,
                club_type,
                club_brand,
                active
            )
        )
        conn.commit()
    st.write('Club Added')
