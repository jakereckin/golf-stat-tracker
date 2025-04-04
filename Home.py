import streamlit as st
import pandas as pd
import sqlitecloud

sql_lite_connect = st.secrets['sqlite_connection']['GOLF_CONNECTION']

sql = """
SELECT * FROM STROKES_GAINED_EXPECTED
"""

def read_sqlite_table(sql, connection):
    with sqlitecloud.connect(connection) as conn:
     return pd.read_sql(sql, conn)

df = read_sqlite_table(sql, sql_lite_connect)
st.write(df)