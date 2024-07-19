import datetime
import numpy as np
import pandas as pd
from typing import Tuple
import streamlit as st


@st.cache_data(ttl=3600)
def download_one_datafile(year='recent') -> Tuple[pd.DataFrame, datetime.datetime]:
    url = 'http://ovh.rencorner.co/mapstats/'
    if year == 'recent':
        url = f'{url}/gamemode.txt'
    else:
        url = f'{url}/gamemode_{year}.txt'
    df = pd.read_csv(url)
    return df, datetime.datetime.now().astimezone()


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    df['Datetime'] = df['Date'].str.strip('[]') + ' ' + df['Time'].str.strip('[]')
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df['Lasted'] = pd.to_datetime(df['Lasted'], format='%H.%M.%S')
    df['LastedMinutes'] = df['Lasted'].dt.hour * 60 + df['Lasted'].dt.minute + df['Lasted'].dt.second / 60.0
    # some rows have "/" at the end of their player count
    df['Players'] = df['Players'].astype(str).str.rstrip('/').astype(int)
    df['PlayersChange'] = df['Players'].diff()
    players_bins = np.array([0, 5, 10, 15, 20, 30, 40, 50, 60])
    df['PlayersBin'] = pd.cut(df['Players'], bins=players_bins)
    df['WinTeamBinary'] = df['WinTeam'].apply(lambda x: 0 if x == 'Nod' else 1)
    df['Mode'] = df['Mode'].str.replace('AOW', 'All Out War')
    df.drop(index=df.loc[~df['Mode'].isin(['Marathon', 'All Out War'])].index, inplace=True)
    df['ModeBinary'] = df['Mode'].apply(lambda x: 0 if x == 'All Out War' else 1)
    df['Map'] = df['Map'].str.replace('.mix', '', regex=False)
    df.rename(columns={'NodPoints': 'Nodpoints'}, inplace=True)
    df = df[[
        'Datetime', 'WinTeam', 'WinTeamBinary', 'Mode', 'ModeBinary', 'WinType', 'Lasted', 'LastedMinutes', 'Map',
        'GDIpoints', 'Nodpoints', 'Players', 'PlayersBin', 'PlayersChange'
    ]]
    return df


def get_data() -> Tuple[pd.DataFrame, datetime.datetime]:
    downloaded_data = [download_one_datafile(year) for year in [2021, 2022, 2023, 'recent']]
    # Uncomment following two lines to d/l one recent data file, for development
    # st.warning('downloading only recent data for development')
    # downloaded_data = [download_one_datafile(year) for year in ['recent']]
    latest_file_datetime = max([dd[1] for dd in downloaded_data])
    latest_file_datetime = latest_file_datetime.replace(microsecond=0)
    all_df = pd.concat([dd[0] for dd in downloaded_data])
    all_df = process_data(all_df)
    return all_df, latest_file_datetime


if __name__ == '__main__':
    get_data()
