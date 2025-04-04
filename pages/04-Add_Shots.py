import streamlit as st
import polars as pl
import pandas as pd
import sqlitecloud
from py import sql

st.header(body='Add Shot', divider='blue')
sql_lite_connect = st.secrets['sqlite_connection']['GOLF_CONNECTION']
with sqlitecloud.connect(sql_lite_connect) as conn:
    db_rounds = pd.read_sql(
        sql=sql.select_rouds_sql(),
        con=conn
    )
    db_clubs = pd.read_sql(
        sql=sql.select_clubs_sql(),
        con=conn
    )
    db_rounds = pl.from_pandas(data=db_rounds)
    db_clubs = pl.from_pandas(data=db_clubs)


round_id = st.selectbox(
    label='Round ID',
    options=db_rounds['ROUND_ID'].to_list()
)
def get_round_info(db_rounds, round_id):
    """
    Retrieves the holes for a given round ID.

    Args:
        db_rounds (DataFrame): The DataFrame containing
        round information.
        round_id (str): The ID of the round to retrieve
        holes for.

    Returns:
        DataFrame: A DataFrame containing the holes
        for the specified round ID.
    """
    this_round = db_rounds.filter(pl.col(name='ROUND_ID') == round_id)
    this_course = this_round['COURSE_NAME'].to_list()[0]
    this_tee = this_round['TEE'].to_list()[0]
    with sqlitecloud.connect(sql_lite_connect) as conn:
        db_holes = pd.read_sql(
            sql=sql.select_holes_sql(),
            con=conn,
            params=(this_course, this_tee)
        )
        db_holes = pl.from_pandas(data=db_holes)
    return this_round, db_holes

def merge_round_info(this_round, db_holes):
    """
    Merges round information with hole information.

    Args:
        this_round (DataFrame): The DataFrame 
        containing round information.
        db_holes (DataFrame): The DataFrame 
        containing hole information.

    Returns:
        DataFrame: A merged DataFrame containing 
        both round and hole information.
    """
    return this_round.join(db_holes, on=['COURSE_NAME', 'TEE'], how='inner')

this_round, db_holes = get_round_info(db_rounds=db_rounds, round_id=round_id)
merged_round_info = merge_round_info(this_round=this_round, db_holes=db_holes)

hole_add = st.selectbox(
    label='Hole',
    options=merged_round_info['HOLE'].to_list()
)
if hole_add:
    hole_par = merged_round_info['PAR'].to_list()[0]
    hole_distance = merged_round_info['DISTANCE'].to_list()[0]
    st.write(f'Hole {hole_add} Par: {hole_par}')
    st.write(f'Hole {hole_add} Distance: {hole_distance}')
    shot_type = st.selectbox(
        label='Shot Type',
        options=['TEE', 'FAIRWAY', 'ROUGH', 'SAND', 'RECOVERY', 'GREEN'],
    )
    if shot_type:
        dist_entry, club_entry = st.columns(spec=2)
        with dist_entry:
            distance = st.number_input(
                label='Distance',
                min_value=0,
                max_value=hole_distance
            )
        with club_entry:
            club = st.selectbox(
                label='Club',
                options=db_clubs['CLUB_NAME'].to_list()
            )
        penalty_entry, make_entry = st.columns(spec=2)
        with penalty_entry:
            penalty_strokes = st.number_input(
                label='Penalty Strokes',
                min_value=0,
                max_value=2
            )
        with make_entry:
            make = st.radio(
                label='Make',
                options=['Yes', 'No'],
                horizontal=True
            )
        add = st.button(label='Add Shot')
        if add:
            with sqlitecloud.connect(sql_lite_connect) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    sql=sql.insert_shot_sql(),
                    parameters=(
                        round_id,
                        hole_add,
                        shot_type,
                        distance,
                        club,
                        penalty_strokes,
                        make
                    )
                )
                conn.commit()
            st.write('Shot Added')