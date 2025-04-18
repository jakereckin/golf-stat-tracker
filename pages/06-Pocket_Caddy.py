import streamlit as st
import polars as pl
import pandas as pd
import sqlitecloud
from py import sql, data_source

st.header(body='Pocket Caddy', divider='blue')

sql_lite_connect = st.secrets['sqlite_connection']['GOLF_CONNECTION']

db_strokes = data_source.run_query(
    sql=sql.read_expected_sql(),
    connection=sql_lite_connect
)

db_strokes = pl.from_pandas(data=db_strokes)

current_distance = st.number_input(
    label='Current Distance',
    min_value=0,
    max_value=400,
    value=0,
    step=1
)

current_shot_type = st.selectbox(
    label='Current Shot Type',
    options=[
        'TEE', 'FAIRWAY', 'ROUGH', 'RECOVERY', 'SAND', 'GREEN'
    ]
)
current_data = db_strokes.filter(
    (pl.col(name='DISTANCE') == current_distance)
)
current_expected = (
    current_data.select(pl.col(name=current_shot_type))
                .rename({current_shot_type: 'EXPECTED'})
                .select('EXPECTED')
)
st.metric(label='Current Expected Strokes Remaining', value=current_expected)


base_distance, base_type = st.columns(spec=2)
with base_distance:
    baseline_distance = st.number_input(
        label='Safe Shot Distance',
        min_value=0,
        max_value=400,
        value=0,
        step=1
    )
with base_type:
    baseline_shot_type = st.selectbox(
        label='Safe Shot Type',
        options=[
            'TEE', 'FAIRWAY', 'ROUGH', 'RECOVERY', 'SAND', 'GREEN'
        ]
    )
baseline_data = db_strokes.filter(
    (pl.col(name='DISTANCE') == baseline_distance)
)
baseline_expeted = (
    baseline_data.select(pl.col(name=baseline_shot_type))
                .rename({baseline_shot_type: 'EXPECTED'})
                .select('EXPECTED')
)

op_one_distance, op_one_type = st.columns(spec=2)
with op_one_distance:
    option_one_distance = st.number_input(
        label='Aggressive Success Distance',
        min_value=0,
        max_value=400,
        value=0,
        step=1
    )
with op_one_type:
    option_one_shot_type = st.selectbox(
        label='Aggressive Success Shot Type',
        options=[
            'TEE', 'FAIRWAY', 'ROUGH', 'RECOVERY', 'SAND', 'GREEN'
        ]
    )
op_two_distance, op_two_type = st.columns(spec=2)

with op_two_distance:
    option_two_distance = st.number_input(
        label='Aggressive Failure Distance',
        min_value=0,
        max_value=400,
        value=0,
        step=1
    )
with op_two_type:
    option_two_shot_type = st.selectbox(
        label='Aggressive Failure Shot Type',
        options=[
            'TEE', 'FAIRWAY', 'ROUGH', 'RECOVERY', 'SAND', 'GREEN'
        ]
    )

option_one_data = db_strokes.filter(
    (pl.col(name='DISTANCE') == option_one_distance)
)
option_one_expected = (
    option_one_data.select(pl.col(name=option_one_shot_type))
                   .rename({option_one_shot_type: 'EXPECTED'})
                   .select('EXPECTED')
)
option_two_data = db_strokes.filter(
    (pl.col(name='DISTANCE') == option_two_distance)
)
option_two_expected = (
    option_two_data.select(pl.col(name=option_two_shot_type))
                   .rename({option_two_shot_type: 'EXPECTED'})
                   .select('EXPECTED')
)
base_ex, one_ex, two_ex = st.columns(spec=3)
with base_ex:
    st.metric(
        label='Safe Shot Expected Strokes Remaining', value=baseline_expeted
    )
with one_ex:
    st.metric(
        label='Aggressive Success Strokes Remaining', value=option_one_expected
    )
with two_ex:
    st.metric(
        label='Aggressive Failure Strokes Remaining', value=option_two_expected
    )

strokes_saved_one = (
    baseline_expeted - option_one_expected
).select('EXPECTED').to_numpy()[0][0]


strokes_save_two = (
    baseline_expeted - option_two_expected
).select('EXPECTED').to_numpy()[0][0]

if strokes_save_two > strokes_saved_one:
    breakeven_probability = (strokes_save_two / (strokes_save_two + strokes_saved_one))
else:
    breakeven_probability = (strokes_saved_one / (strokes_save_two + strokes_saved_one))

st.metric(
    label='Sucess rate needed for aggressive option',
    value=f'{breakeven_probability:.2%}'
)