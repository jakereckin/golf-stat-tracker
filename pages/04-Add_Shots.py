import streamlit as st
import polars as pl
import pandas as pd
import sqlitecloud
from py import sql, data_source

st.header(body='Add Shot', divider='blue')
sql_lite_connect = st.secrets['sqlite_connection']['GOLF_CONNECTION']
db_rounds = data_source.run_query(
    sql=sql.select_rouds_sql(),
    connection=sql_lite_connect
)
db_clubs = data_source.run_query(
    sql=sql.select_clubs_sql(),
    connection=sql_lite_connect
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
    db_holes = data_source.run_query(
        sql=sql.select_holes_sql(),
        connection=sql_lite_connect,
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


def get_shots_in_round(merged_round_info):
    """
    Retrieves the shots in a round.

    Args:
        merged_round_info (DataFrame): The DataFrame 
        containing merged round and hole information.

    Returns:
        DataFrame: A DataFrame containing the shots 
        in the round.
    """
    shots_in_round = data_source.run_query(
        sql=sql.read_shots_sql(),
        connection=sql_lite_connect,
        params=(merged_round_info['ROUND_ID'].to_list()[0],)
    )
    shots_in_round = pl.from_pandas(data=shots_in_round)
    return shots_in_round


this_round, db_holes = get_round_info(db_rounds=db_rounds, round_id=round_id)
merged_round_info = merge_round_info(this_round=this_round, db_holes=db_holes)
shots_in_round = get_shots_in_round(merged_round_info=merged_round_info)

hole_add = st.selectbox(
    label='Hole',
    options=merged_round_info['HOLE'].to_list(),
    placeholder='Select Hole',
    index=None
)
if hole_add:
    shots_in_round = get_shots_in_round(merged_round_info=merged_round_info)
    st.write(merged_round_info)
    merged_round_info = merged_round_info.with_columns(
        pl.col(name='HOLE').cast(pl.Int32)
    )
    hole_add = int(hole_add)
    this_hole = merged_round_info.filter(
        pl.col(name='HOLE') == hole_add
    )
    hole_par = this_hole['PAR'].to_list()[0]
    hole_distance = this_hole['DISTANCE'].to_list()[0]
    par, distance = st.columns(spec=2)
    with par:
        st.write(f'Hole {hole_add} Par: {hole_par}')
    with distance:
        st.write(f'Hole {hole_add} Distance: {hole_distance}')
    shots_in_round = shots_in_round.with_columns(
         pl.col(name='HOLE').cast(pl.Int32)
    )
    if len(shots_in_round['HOLE']) == 0:
         data = {
              'HOLE': '',
              'SHOT_NUMBER': '',
                'SHOT_TYPE': '',
                'DISTANCE': '',
                'CLUB': ''
         }
         last_shot = pl.DataFrame(data=[data])
         max_shot = 1
    else:      
        hole_data = shots_in_round.filter(
            pl.col(name='HOLE') == int(hole_add)
        )
        max_shot = hole_data['SHOT_NUMBER'].max()
        if max_shot is None:
            max_shot = 1
        else:
            max_shot += 1
        last_shot = shots_in_round.filter(
            pl.col(name='HOLE') == int(hole_add)
        ).filter(
            pl.col(name='SHOT_NUMBER') == max_shot - 1
        )
    st.dataframe(last_shot[['HOLE', 'SHOT_NUMBER', 'SHOT_TYPE', 'DISTANCE', 'CLUB']])
    sht_type, number = st.columns(spec=2)
    with sht_type:
        shot_type = st.radio(
            label='Shot Type',
            options=['TEE', 'FAIRWAY', 'ROUGH', 'SAND', 'RECOVERY', 'GREEN'],
            horizontal=True
        )
    with number:
        shot_number = st.number_input(
            label='Shot Number',
            min_value=1,
            max_value=20,
            value=max_shot
            )
    if shot_number:
        dist_entry, club_entry = st.columns(spec=2)
        with dist_entry:
            init_value = 0
            if shot_number == 1:
                init_value = hole_distance
            distance = st.number_input(
                    label='Distance',
                    min_value=0,
                    max_value=hole_distance + 100,
            )
        with club_entry:
                club = st.radio(
                    label='Club',
                    options=db_clubs['CLUB_NAME'].to_list(),
                    horizontal=True
                )
        miss_type, putt_type = st.columns(spec=2)
        penalty_entry, make_entry = st.columns(spec=2)
        with miss_type:
                miss_shot_types = ['RIGHT', 'LEFT', 'LONG', 'SHORT', 'HIT']
                miss_shot = st.radio(
                    label='Missed Shot Type',
                    options=miss_shot_types,
                    horizontal=True
                )
        with putt_type:
                putt_shot_types = [
                    'U-LR', 'U-RL', 'U-S', 
                    'D-LR', 'D-RL', 'D-S',
                    'F-LR', 'F-RL', 'F-S'
                ]
                putt_shot = st.radio(
                    label='Putt Shot Type',
                    options=putt_shot_types,
                    horizontal=True
                )
        with penalty_entry:
                penalty_strokes = st.number_input(
                    label='Penalty Strokes',
                    min_value=0,
                    max_value=2
                )
        with make_entry:
                make = st.radio(
                    label='Make',
                    options=['No', 'Yes'],
                    horizontal=True, 

                )
        add = st.button(label='Add Shot')
        if add:
            with sqlitecloud.connect(sql_lite_connect) as conn:
                if shot_type != 'GREEN':
                    putt_type = 'N/A'
                cursor = conn.cursor()
                hole_add = str(hole_add)
                shot_number = int(shot_number)
                round_id = str(round_id)
                shot_type = str(shot_type)
                distance = int(distance)
                penalty_strokes = int(penalty_strokes)
                club = str(club)
                miss_type = str(miss_shot)
                putt_shot = str(putt_shot)
                make = str(make)
                cursor.execute(
                        sql=sql.insert_shot_sql(),
                        parameters=(
                            round_id,
                            hole_add,
                            shot_number,
                            shot_type,
                            distance,
                            club,
                            penalty_strokes,
                            miss_type,
                            putt_shot,
                            make
                        )
                )
                conn.commit()
            st.write('Shot Added')
            st.rerun()