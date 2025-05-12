import streamlit as st
import polars as pl
import pandas as pd
import numpy as np
from py import sql, data_source

st.header(body='Strokes Gained', divider='blue')
sql_lite_connect = st.secrets['sqlite_connection']['GOLF_CONNECTION']

db_rounds = data_source.run_query(
    sql=sql.select_rounds_sql(),
    connection=sql_lite_connect
)
db_strokes = data_source.run_query(
    sql=sql.read_expected_sql(),
    connection=sql_lite_connect
)
db_shots = data_source.run_query(
    sql=sql.read_shots_sql(),
    connection=sql_lite_connect
)
db_strokes = pl.from_pandas(data=db_strokes)
db_rounds = pl.from_pandas(data=db_rounds)
db_shots = pl.from_pandas(data=db_shots)
db_shots = db_shots.with_columns(
    db_shots.sort(['ROUND_ID', 'HOLE', 'SHOT_NUMBER'])
            .groupby(['ROUND_ID', 'HOLE']) 
            .apply(lambda df: df.with_columns(
                pl.col(name='DISTANCE')
                  .shift(periods=-1)
                  .fill_null(value=0)
                  .alias(name='FINAL_DISTANCE'),
                pl.col('SHOT_TYPE')
                  .shift(periods=-1)
                  .fill_null(value='MAKE')
                  .alias(name='FINAL_SHOT_TYPE')
                )
            )
)
db_shots = db_shots.sort(['ROUND_ID', 'HOLE', 'SHOT_NUMBER'])
db_strokes_unpivot = db_strokes.melt(
    id_vars=['DISTANCE'],
    value_vars=[
        'TEE',
        'FAIRWAY',
        'ROUGH',
        'RECOVERY',
        'SAND',
        'GREEN'
    ],
    variable_name='SHOT_TYPE',
    value_name='EXPECTED'
)
db_shots_join = db_shots.join(
    db_strokes_unpivot,
    on=['DISTANCE', 'SHOT_TYPE'],
    how='left'
)
db_shots_join = db_shots_join.rename(
    dict(
        EXPECTED='START_EXPECTED'
    )
)
db_shots_join = db_shots_join.join(
    db_strokes_unpivot,
    left_on=['FINAL_DISTANCE', 'FINAL_SHOT_TYPE'],
    right_on=['DISTANCE', 'SHOT_TYPE'],
    how='left'
)
db_shots_join = db_shots_join.rename(
    dict(
        EXPECTED='FINAL_EXPECTED'
    )
)
db_shots_join = db_shots_join.with_columns(
    pl.col(name='FINAL_EXPECTED')
      .fill_null(value=0)
      .alias(name='FINAL_EXPECTED')
)
db_shots_join = db_shots_join.with_columns(
    STROKES_GAINED=(pl.col('START_EXPECTED')-pl.col('FINAL_EXPECTED') - 1)
)
db_shots_join = db_shots_join.with_columns(
    STROKES_GAINED=pl.col('STROKES_GAINED')-pl.col('PENALTY_STROKES')
)
db_shots_join_copy = db_shots_join

my_rounds = st.selectbox(
    label='Select Round',
    options=db_rounds['ROUND_ID'].to_list(),
    index=None,
    placeholder='Select Round'
)
if my_rounds:
    this_round = db_shots_join.filter(
        pl.col(name='ROUND_ID') == my_rounds
    )
    this_round = this_round.sort(
        by=['STROKES_GAINED']
    )
    keep_worst = this_round.head(n=10)
    keep_worst = keep_worst.select(
        'HOLE', 'SHOT_NUMBER', 'DISTANCE', 'CLUB', 'STROKES_GAINED'
    )
    group_holes = this_round.groupby(by='HOLE').agg(
        HOLE_SCORE=pl.col('SHOT_NUMBER').max()
    )
    total_score = group_holes['HOLE_SCORE'].sum()
    total_expected = this_round.filter(
        pl.col('SHOT_NUMBER') == 1
    )
    total_expected = total_expected['START_EXPECTED'].sum()
    total_expected = np.round(total_expected, decimals=2)
    actual, expected = st.columns(2)
    with actual:
        st.metric(value=total_score, label='Total Shots Taken')
    with expected:
        st.metric(value=total_expected, label='Total Expected Shots')

    green_not = st.radio(
        label='Strokes Gained View',
        options=['Putt', 'Full Shot', 'Club', 'Shot Type'],
        horizontal=True
    )
    if green_not == 'Putt':

        def _putting_distances(distance):
            if distance <= 5:
                return '(0) 0-5 Feet'
            elif distance <= 10:
                return '(1) 5-10 Feet'
            elif distance <= 15:
                return '(2) 10-15 Feet'
            elif distance <= 20:
                return '(3) 15-20 Feet'
            elif distance <= 30:
                return '(4) 20-30 Feet'
            elif distance <= 50:
                return '(5) 30-50 Feet'
            else:
                return '(6) 50+ Feet'

        this_round = this_round.filter(
            pl.col(name='SHOT_TYPE') == 'GREEN'
        )
        this_round = this_round.with_columns(
            PUTTING_DISTANCE=pl.col(name='DISTANCE').apply(_putting_distances)
        )
        putting_distance = (
            this_round.groupby(by=['PUTTING_DISTANCE'])
                      .agg(
                          STROKES_GAINED=pl.col(name='STROKES_GAINED').sum(),
                          COUNT=pl.col(name='STROKES_GAINED').count()
                      )
                      .sort(by=['PUTTING_DISTANCE'], descending=False)
        )
        st.write(putting_distance)
    elif green_not == 'Full Shot':

        def _yard_distances(distance):
            if distance <= 40:
                return '(0) 0-40 Yards'
            elif distance <= 60:
                return '(1) 40-60 Yards'
            elif distance <= 75:
                return '(2) 60-75 Yards'
            elif distance <= 100:
                return '(3) 75-100 Yards'
            elif distance <= 125:
                return '(4) 100-125 Yards'
            elif distance <= 150:
                return '(5) 125-150 Yards'
            elif distance <= 175:
                return '(6) 150-175 Yards'
            elif distance <= 200:
                return '(7) 175-200 Yards'
            elif distance <= 225:
                return '(8) 200-225 Yards'
            elif distance <= 250:
                return '(9) 225-250 Yards'
            elif distance <= 300:
                return '(91) 250-300 Yards'
            else:
                return '(92) 300+ Yards'
                

        this_round = this_round.filter(
            pl.col(name='SHOT_TYPE') != 'GREEN'
        )
        this_round = this_round.with_columns(
            YARDAGE=pl.col(name='DISTANCE').apply(_yard_distances)
        )
        yardage = (
            this_round.groupby(by=['YARDAGE'])
                      .agg(
                          STROKES_GAINED=pl.col(name='STROKES_GAINED').sum(),
                          COUNT=pl.col(name='STROKES_GAINED').count()
                      )
                      .sort(by=['YARDAGE'], descending=False)
        )
        st.write(yardage)

    elif green_not == 'Shot Type':
        strokes_gained = (
            this_round.groupby(by=['SHOT_TYPE'])
                      .agg(
                          STROKES_GAINED=pl.col(name='STROKES_GAINED').sum(),
                          COUNT=pl.col(name='STROKES_GAINED').count()
                      )
                      .sort(by=['COUNT'], descending=True)
        )
        st.write(strokes_gained)
    else:
        strokes_gained_club = (
        this_round.groupby(by=['CLUB'])
                  .agg(
                      STROKES_GAINED=pl.col(name='STROKES_GAINED').sum(),
                      COUNT=pl.col(name='STROKES_GAINED').count()
                  )
                  .sort(by=['COUNT'], descending=True)
        )
        st.write(strokes_gained_club)

    st.write('10 Worst Shots')
    st.dataframe(keep_worst, use_container_width=True, hide_index=True)