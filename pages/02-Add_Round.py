import streamlit as st
import polars as pl
import pandas as pd
import sqlitecloud
from py import sql, data_source

st.header(body='Add Round', divider='blue')
sql_lite_connect = st.secrets['sqlite_connection']['GOLF_CONNECTION']

db_courses = data_source.run_query(
    sql=sql.get_courses_sql(),
    connection=sql_lite_connect
)
db_courses = pl.from_pandas(db_courses)

date = st.date_input(
    label='Date',
    value=pd.to_datetime('today').date()
)
tee_time = st.time_input(
    label='Tee Time',
    value=pd.to_datetime('12:00').time()
)
course_name = st.selectbox(
    label='Course Name',
    options=db_courses['COURSE_NAME'].to_list()
)
if course_name:
    this_course = db_courses.filter(
        pl.col(name='COURSE_NAME') == course_name
    )
    tee = st.selectbox(
        label='Tee',
        options=this_course['TEE'].to_list()
    )
holes = st.radio(
    label='Number of Holes',
    options=[9, 18],
    horizontal=True
)
add_round = st.button(label='Add Round')

if add_round:
    with sqlitecloud.connect(sql_lite_connect) as conn:
        cursor = conn.cursor()
        date = str(date)
        tee_time = str(tee_time)
        holes = int(holes)
        round_id = (
            course_name 
            + '_' 
            + date 
            + '_' 
            + tee 
            + '_' 
            + tee_time 
            + '_' 
            + str(holes)
        )
        cursor.execute(
            sql=sql.insert_round_sql(),
            parameters=(
                    course_name,
                    tee,
                    date,
                    tee_time,
                    round_id,
                    holes
            )
        )
        conn.commit()
    st.write('Round Added')