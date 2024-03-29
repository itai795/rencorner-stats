import datetime
import pytz
import streamlit as st
from src.about_tab import write_about_tab
from src.data_utils import slice_player_count, slice_dates
from src.get_data import get_data
from src.plots import plot_players_over_time
from src.win_rate_tab import write_win_rate_tab


def main_page():
    st.title('RenCorner Online Stats Tool')
    # For development: all_data_container displays the downloaded data
    # all_data_container = st.container()
    wr_tab, pc_tab, set_tab, about_tab = st.tabs(['Win rate :bar_chart:', 'Player count :chart_with_upwards_trend:',
                                                  'Data settings :gear:', 'About :information_source:'])
    df, latest_file_datetime = get_data()
    # all_data_container.dataframe(df)
    with set_tab:
        df = slice_dates(df)
        timezone_help_msg = """
        Original dates and times are in US Eastern Time. When transitioning between Standard and Daylight Saving Time,
         you may notice "jumps" of -1 or +1 hour between match end times. Enabling Europe Central Time will mitigate
         these discrepancies.
        However, please note that some inconsistencies in match end times may still occur during Standard/Daylight
         Saving Time conversions.  
        """
        tz_europe = st.checkbox('Use Europe Central Time', value=False, help=timezone_help_msg)
        if tz_europe:
            df['Datetime'] = df['Datetime'].dt.tz_localize('America/New_York', ambiguous='infer')
            df['Datetime'] = df['Datetime'].dt.tz_convert('Europe/Brussels')
            latest_file_datetime = latest_file_datetime.astimezone(tz=pytz.timezone('Europe/Brussels'))
        else:
            latest_file_datetime = latest_file_datetime.astimezone(tz=pytz.timezone('America/New_York'))
    with pc_tab:
        plot_players_over_time(df)
    with wr_tab:
        df_wr = slice_player_count(df)
        write_win_rate_tab(df=df_wr)
    with about_tab:
        latest_match = df['Datetime'].max()
        write_about_tab(latest_file_datetime=latest_file_datetime, latest_match=latest_match)
