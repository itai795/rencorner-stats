import datetime
from itertools import product
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import streamlit as st

DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


# def time_binning_and_plot(df1, bin_column, plot='percentile', percentiles=[25, 50, 75]):
#     def agg_percentile(n):
#         def percentile_(x):
#             return np.percentile(x, n)
#
#         percentile_.__name__ = 'percentile_%s' % n
#         return percentile_
#
#     def multiindex_to_index(x):
#         # Turn the ['weekday_bin', '1h_bin'] multindex with 2 sub-indices into 1.
#         return f"{weekday_to_dayname[x[0]]} {x[1]}:00"
#
#     weekday_to_dayname = {i: day_name for i, day_name in enumerate(DAY_NAMES)}
#
#     if isinstance(bin_column, list):
#         df_time_grouped = df1.groupby(by=bin_column).aggregate({
#             'Players': ['mean', 'std', 'max', agg_percentile(25), agg_percentile(50), agg_percentile(75)]
#         })['Players']
#         df_time_grouped.reset_index(inplace=True)
#         df_time_grouped['weekly_hourly_bin'] = np.arange(df_time_grouped.shape[0])
#         bin_column = 'weekly_hourly_bin'
#     else:
#         df_time_grouped = df1.groupby(by=bin_column).aggregate({
#             'Players': ['mean', 'std', 'max', agg_percentile(25), agg_percentile(50), agg_percentile(75)]
#         })['Players']
#         if bin_column in ['weekday_bin', 'Date']:
#             df_time_grouped[bin_column] = df_time_grouped.index
#         else:
#             df_time_grouped[bin_column] = df_time_grouped.index.astype(str)
#         if bin_column == 'weekday_bin':
#             df_time_grouped['weekday_bin'] = df_time_grouped['weekday_bin'].replace(weekday_to_dayname)
#
#     if plot == 'mean_max':
#         layout = df_time_grouped.hvplot.scatter(x=bin_column, y='mean')
#         layout *= hv.ErrorBars((df_time_grouped[bin_column], df_time_grouped['mean'], df_time_grouped['std']))
#     elif plot == 'percentile':
#         layout = hv.Overlay()
#         for per in percentiles:
#             layout *= df_time_grouped.hvplot.scatter(x=bin_column, y=f'percentile_{per}', label=f'percentile {per}')
#     elif plot == 'line_percentile':
#         layout = df_time_grouped.hvplot.line(x=bin_column, y='percentile_75', label='percentile 75')
#     elif plot == 'area_percentiles':
#         layout = df_time_grouped.hvplot.area(x=bin_column, y='percentile_25', y2='percentile_75') \
#                  .opts(alpha=0.2, tools=[])
#         for per in percentiles:
#             line_dash = 'solid' if per == 50 else 'dotted'
#             line_alpha = 1 if per == 50 else 0.5
#             layout *= df_time_grouped.hvplot.line(x=bin_column, y=f'percentile_{per}') \
#                       .opts(color=Category10_10[0], line_dash=line_dash, alpha=line_alpha)
#     return layout


def plot_players_over_time(df: pd.DataFrame):
    # Preprocessing
    df_time = df.copy()
    df_time['1h_bin'] = df_time['Datetime'].dt.hour
    df_time['weekday_bin'] = df_time['Datetime'].dt.day_of_week
    with warnings.catch_warnings():
        # df_time['Datetime'].dt.date is an object column, subtracting with a TimeDelta column promotes a
        #   PerformanceWarning
        warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
        df_time['week_start_bin'] = \
            df_time['Datetime'].dt.date - pd.to_timedelta(df_time['Datetime'].dt.day_of_week, unit='d')

    # Plot player count last week
    df_to_plot = df_time.loc[df_time['Datetime'].dt.date >= datetime.date.today() - datetime.timedelta(days=7)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_to_plot['Datetime'], y=df_to_plot['Players'],
        hovertemplate='Players: %{y}' + '<br>Date: %{x}'
    ))
    fig.update_layout(title='Players last week', xaxis_title='Date and Time', yaxis_title='Player count')
    fig.update_xaxes(showgrid=True)
    st.plotly_chart(fig)

    df_to_plot = df_time.loc[df_time['Datetime'].dt.date >= datetime.date.today() - datetime.timedelta(days=30)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_to_plot['Datetime'], y=df_to_plot['Players'],
        hovertemplate='Players: %{y}' + '<br>Date: %{x}'
    ))
    fig.update_layout(title='Players last week', xaxis_title='Date and Time', yaxis_title='Player count')
    fig.update_xaxes(showgrid=True)
    st.plotly_chart(fig)

    st.info('More to come')
    return
    # Below is WIP

    # # Plot player count by hour
    # plot_hvplot(
    #     time_binning_and_plot(df_time, '1h_bin', plot='area_percentiles')
    #     .opts(title='Players count by hour', xlabel='Hour', ylabel='Player count', show_grid=True),
    #     height=400
    # )
    #
    # # Plot player count along the week
    # xticks = [(i*12, f'{dayname} {hour}') for i, (dayname, hour) in enumerate(product(DAY_NAMES, ['0:00', '12:00']))]
    # plot_hvplot(
    #     time_binning_and_plot(df_time, ['weekday_bin', '1h_bin'], plot='area_percentiles')
    #     .opts(title='Players count along week', xlabel='Day Hour', ylabel='Player count',
    #           xrotation=45, show_grid=True, xticks=xticks),
    #     height=400
    # )
    #
    # # Plot player count timeline
    # time_slice = st.slider('Select time range to filter data (default: 13:00 to 22:00 Eastern)',
    #                        0, 24, value=(13, 22))
    # st.write('Concentrating on hours between 13 to 22')
    # plot_hvplot(
    #     time_binning_and_plot(df_time.loc[(df_time['1h_bin'] >= time_slice[0]) & (df_time['1h_bin'] <= time_slice[1])],
    #                           'Date', plot='area_percentiles') \
    #     .opts(title='Players count by date', xlabel='Date', ylabel='Player count', xrotation=45,
    #           show_grid=True),
    #     height=400
    # )


def plot_win_rates(wr_df: pd.DataFrame, mode_display: str, gdi_win_rate: int):
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.6, 1.0],
        specs=[[{"type": "bar"}], [{"type": "bar"}]],
        vertical_spacing=0.02,
        shared_xaxes=True,
    )
    fig.add_trace(
        go.Bar(x=wr_df['Map'], y=wr_df['Count'],
               hovertemplate='Map: %{x}' + '<br>Count: %{y}', name=''),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=wr_df['Map'], y=wr_df['GDI'],
               marker={'color': 'goldenrod'},
               hovertemplate='Map: %{x}' + '<br>Win Rate: %{y:.1f}', name=''),
        row=2, col=1
    ),
    fig.add_trace(
        go.Bar(x=wr_df['Map'], y=wr_df['Nod'],
               marker={'color': 'darkred'},
               hovertemplate='Map: %{x}' + '<br>Win Rate: %{y:.1f}', name=''),
        row=2, col=1
    )

    fig.update_layout(
        title=f'Map count and win rate[%],'
              f' {mode_display}, mean: {gdi_win_rate}-{100 - gdi_win_rate} (GDI-Nod)',
        barmode='stack', showlegend=False, height=600
    )
    fig.update_xaxes(tickangle=80)

    # adding grid lines (there is probably a better way to set it using builtin grid)
    for hline_height in range(10, 100, 10):
        line_width = 2 if hline_height == 50 else 1
        opacity = 0.4 if hline_height == 50 else 0.2
        fig.add_hline(y=hline_height, line_width=line_width, opacity=opacity, row=2)

    st.plotly_chart(fig, config={'modeBarButtonsToRemove': ['zoom', 'pan', 'select2d', 'lasso2d', 'zoomIn2d',
                                                            'zoomOut2d', 'autoScale2d', 'resetScale2d']})
