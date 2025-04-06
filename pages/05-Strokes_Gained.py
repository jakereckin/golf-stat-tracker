import streamlit as st
import polars as pl
import pandas as pd
import numpy as np
from py import sql, data_source

st.header(body='Strokes Gained', divider='blue')
sql_lite_connect = st.secrets['sqlite_connection']['GOLF_CONNECTION']

db_rounds = data_source.run_query(
    sql=sql.select_rouds_sql(),
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
    strokes_gained = this_round.groupby(by=['SHOT_TYPE']).agg(
        pl.col(name='STROKES_GAINED').sum().alias(name='STROKES_GAINED')
    )
    total_score = this_round['SHOT_NUMBER'].value_counts().sum()
    total_score = total_score['counts'].to_list()[0]
    total_expected = this_round.filter(
        pl.col('SHOT_NUMBER') == 1
    )
    total_expected = total_expected['START_EXPECTED'].sum()
    total_expected = np.round(total_expected, decimals=2)

    st.metric(value=total_score, label='Total Shots Taken')
    st.metric(value=total_expected, label='Total Expected Shots')
    st.write(strokes_gained)