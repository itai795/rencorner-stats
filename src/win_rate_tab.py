import numpy as np
import pandas as pd
import streamlit as st
from src.data_utils import select_maps
from src.plots import plot_win_rates


def write_win_rate_tab(df: pd.DataFrame):
    st.header('Win Rates')
    # Preprocess
    if df.empty:
        return
    df_wr = df.copy()
    df_wr = df_wr.loc[(df_wr['Mode'] == 'Marathon') | (df_wr['Mode'] == 'All Out War')]
    df_wr = select_maps(df_wr)
    df_wr = df_wr.loc[df_wr['WinType'] != 'Server Shutdown']
    df_wr = df_wr.loc[df_wr['Map'] != 'C&C_Walls_G_b10']  # GDI vs GDI map - pointless to analyze here
    df_grouped_map_and_mode = df_wr.groupby(by=['Map', 'Mode'])
    df_grouped_map_and_mode = df_grouped_map_and_mode.aggregate({'WinTeamBinary': ['mean', 'count']})
    # # flatten columns
    df_grouped_map_and_mode['GDI_Win_Rate'] = df_grouped_map_and_mode['WinTeamBinary']['mean']
    df_grouped_map_and_mode['Count'] = df_grouped_map_and_mode['WinTeamBinary']['count']
    df_grouped_map_and_mode.drop(columns=['WinTeamBinary'], inplace=True)
    df_grouped_map_and_mode.columns = [col[0] for col in df_grouped_map_and_mode.columns]
    # # flattening done
    df_grouped_map_and_mode['Map'] = [ind[0] for ind in df_grouped_map_and_mode.index.values]
    df_grouped_map_and_mode['Mode'] = [ind[1] for ind in df_grouped_map_and_mode.index.values]
    df_grouped_map_and_mode['Map_Mode'] = \
        df_grouped_map_and_mode['Map'].str[4:] + '_' \
        + df_grouped_map_and_mode['Mode'].apply(lambda x: 'AoW' if x == 'All Out War' else x)
    df_grouped_map_and_mode['GDI'] = 100 * df_grouped_map_and_mode['GDI_Win_Rate']
    df_grouped_map_and_mode['Nod'] = 100 - df_grouped_map_and_mode['GDI']
    df_grouped_map_and_mode = df_grouped_map_and_mode[['Map', 'Mode', 'Map_Mode', 'GDI', 'Nod', 'Count']]
    df_grouped_map_and_mode.loc[df_grouped_map_and_mode['Mode'] == 'All Out War', 'GDI AoW'] = \
        df_grouped_map_and_mode.loc[df_grouped_map_and_mode['Mode'] == 'All Out War', 'GDI']
    df_grouped_map_and_mode.loc[df_grouped_map_and_mode['Mode'] == 'All Out War', 'Nod AoW'] = \
        df_grouped_map_and_mode.loc[df_grouped_map_and_mode['Mode'] == 'All Out War', 'Nod']
    df_grouped_map_and_mode.loc[df_grouped_map_and_mode['Mode'] == 'Marathon', 'GDI Mar'] = \
        df_grouped_map_and_mode.loc[df_grouped_map_and_mode['Mode'] == 'Marathon', 'GDI']
    df_grouped_map_and_mode.loc[df_grouped_map_and_mode['Mode'] == 'Marathon', 'Nod Mar'] = \
        df_grouped_map_and_mode.loc[df_grouped_map_and_mode['Mode'] == 'Marathon', 'Nod']
    df_grouped_map_and_mode.reset_index(drop=True, inplace=True)
    df_grouped_map_and_mode.sort_values(by=['Mode', 'Nod'], inplace=True)

    # Plot
    df_grouped_map_mara = df_grouped_map_and_mode.loc[df_grouped_map_and_mode['Mode'] == 'Marathon']
    if df_grouped_map_mara.empty:
        st.text('No Marathon maps for the selected criteria')
    else:
        gdi_win_rate = int(np.round(df_grouped_map_mara['GDI'].mean()))
        plot_win_rates(mode_display='Marathon', wr_df=df_grouped_map_mara, gdi_win_rate=gdi_win_rate)

    df_grouped_aow_mara = df_grouped_map_and_mode.loc[df_grouped_map_and_mode['Mode'] == 'All Out War']
    if df_grouped_aow_mara.empty:
        st.text('No AoW maps for the selected criteria')
    else:
        gdi_win_rate = int(np.round(df_grouped_aow_mara['GDI'].mean()))
        plot_win_rates(mode_display='AoW', wr_df=df_grouped_aow_mara, gdi_win_rate=gdi_win_rate)
