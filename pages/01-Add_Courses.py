import streamlit as st
import pandas as pd
import sqlitecloud
from py import sql, data_source

st.header(body='Add Course', divider='blue')
sql_lite_connect = st.secrets['sqlite_connection']['GOLF_CONNECTION']
holes = st.radio(
    label='Number of Holes', options=[9, 18], horizontal=True
)
if holes == 9:
    num_holes = 9
else:
    num_holes = 18


if holes:
    course_name = st.text_input(label='Course Name')
    if course_name: 
        tee = st.text_input(label='Tee')
        if tee:
            holes_data = []
            for hole in range(1, num_holes + 1):
                col1, col2, col3 = st.columns(spec=3)
                with col1:
                    par = st.number_input(
                        label=f'Hole {hole} Par', 
                        min_value=0,
                        key=f'par_{hole}'
                    )
                with col2:
                    distance = st.number_input(
                        label=f'Hole {hole} Distance (yards)',
                        min_value=0,
                        key=f'distance_{hole}'
                    )
                holes_data.append(
                    {'hole': hole, 'par': par, 'distance': distance}
                )
        add = st.button(label='Add Course')

        if add:
            with sqlitecloud.connect(connection_str=sql_lite_connect) as conn:
                cursor = conn.cursor()
                cursor.execute(sql=sql.create_course_sql())
                for hole in holes_data:
                    cursor.execute(
                        sql=sql.insert_course_sql(),
                        parameters=(
                            course_name, 
                            tee, 
                            hole['hole'], 
                            hole['par'], 
                            hole['distance']
                        )
                    )
                conn.commit()
            st.write('Course Added')
