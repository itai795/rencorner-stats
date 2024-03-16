import datetime
import pandas as pd
import streamlit as st


def slice_player_count(df: pd.DataFrame) -> pd.DataFrame:
    min_players = st.slider('Minimum player count selection, default=6', value=6, min_value=1, max_value=60,
                            help='Please select the minimum number of players at the end of each match to proceed with'
                                 ' the analysis below')
    df = df.loc[df['Players'] >= min_players]
    return df


def select_maps(df: pd.DataFrame) -> pd.DataFrame:
    """Presents the user a list of maps inside a table and let him choose which to filter out
    """
    st.write("Choose the maps you'd like to continue analyzing by checking the corresponding boxes.")
    map_counts = df.groupby(['Map', 'Mode']).count()[['Datetime']]
    map_counts.reset_index(inplace=True)
    map_counts.rename(columns={'Datetime': 'Count'}, inplace=True)
    map_counts = map_counts.pivot(columns='Mode', index='Map', values='Count')
    modes = map_counts.columns
    map_counts.reset_index(inplace=True)
    map_counts.fillna(0, inplace=True)
    map_counts[modes] = map_counts[modes].astype(int)
    map_counts['Total count'] = map_counts[modes].sum(axis=1)
    map_counts.rename(columns={'All Out War': 'All Out War count', 'Marathon': 'Marathon count'}, inplace=True)
    default_map_count_to_display = 15 if map_counts['Total count'].max() >= 15 else 5
    map_counts['Selected'] = map_counts.apply(lambda row: row['Total count'] >= default_map_count_to_display, axis=1)
    map_counts.drop(columns=['Total count'], inplace=True)
    map_counts_ret = st.data_editor(map_counts, hide_index=True, use_container_width=True)
    df = df.loc[df['Map'].isin(map_counts_ret.loc[map_counts_ret['Selected'], 'Map'])]
    return df


def slice_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Let the user choose what dates he is interested with
    """
    df['Date'] = df['Datetime'].dt.date
    date_range_selection = st.selectbox(
        'Select date range',
        options=['Last week', 'Last month', 'Last year', 'All time', 'Custom'], index=2
    )
    if date_range_selection == 'Custom':
        min_date = df['Date'].min()
        max_date = df['Date'].max()
        start_date = st.date_input('Start date', value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input('End date', value=max_date, min_value=min_date, max_value=max_date)
        df = df.loc[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    else:
        date_today = datetime.date.today()
        if date_range_selection == 'Last week':
            start_date = date_today - datetime.timedelta(days=7)
        elif date_range_selection == 'Last month':
            start_date = date_today - datetime.timedelta(days=30)
        elif date_range_selection == 'Last year':
            start_date = datetime.date(date_today.year - 1, date_today.month, date_today.day)
        elif date_range_selection == 'All time':
            start_date = datetime.date(2000, 1, 1)
        df = df.loc[df['Date'] >= start_date]
    return df
