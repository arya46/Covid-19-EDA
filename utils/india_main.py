import plotly.graph_objects as go
import numpy as np

def plot_india_trend_CAD(cases_ts):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=cases_ts['Date'], y=cases_ts['Total Deceased'], fill='tozeroy', \
                            name='Death Cases', line_color='red')) # fill down to xaxis
    fig.add_trace(go.Scatter(x=cases_ts['Date'], y=cases_ts['Total Recovered'], fill='tonexty', \
                            name='Recovered Cases', line_color='green')) # fill to trace0 y
    fig.add_trace(go.Scatter(x=cases_ts['Date'], y=cases_ts['Total Confirmed'], fill='tonexty', \
                            name='Confirmed Cases', line_color='blue')) # fill to trace0 y

        
    fig.update_layout(
        xaxis=dict(
            mirror=True,
            ticks='outside',
            showline=True,
            linecolor='black',
        ),
        yaxis=dict(
            mirror=True,
            ticks='outside',
            showline=True,
            linecolor='black',
            gridcolor='LightGrey'
        ),
        legend=dict(x=0.01, y=0.98),
    )

    annotations = []

    # Title
    annotations.append(dict(xref='paper', yref='paper', 
                            x=0.0, y=1.05,
                            xanchor='left', yanchor='bottom',
                            text='COVID-19 cases over time in India',
                            font=dict(family='Arial',
                                    size=12,
                                    color='rgb(37,37,37)'),
                            showarrow=False))

    fig.update_layout(annotations=annotations, plot_bgcolor='white', hovermode='x', autosize=True)

    return fig

def plot_india_daily_confirmed(cases_ts):
    fig = go.Figure(data=[go.Bar(x=cases_ts['Date'],y=cases_ts['Daily Confirmed'])])
    fig.update_layout(
        title='New Confirmed Cases Over Time in India',
        font_size=10,
        xaxis_tickfont_size=14,
        xaxis=dict(
            ticks='outside',
            showline=True,
            linecolor='black',
        ),
        yaxis=dict(
            title='# of confirmed cases',
            titlefont_size=14,
            tickfont_size=14,
            gridcolor='LightGrey',
            ticks='outside',
            showline=True,
            linecolor='black',
        ),

        plot_bgcolor='white',
        autosize=True
    )
    return fig

def plot_india_daily_deaths(cases_ts):
    fig = go.Figure(data=[go.Bar(x=cases_ts['Date'],y=cases_ts['Daily Deceased'])])
    fig.update_traces(marker_color='indianred')
    fig.update_layout(
        title='New Death Cases Over Time in India',
        font_size=10,
        xaxis_tickfont_size=14,
        xaxis=dict(
            ticks='outside',
            showline=True,
            linecolor='black',
        ),
        yaxis=dict(
            title='# of death cases',
            titlefont_size=14,
            tickfont_size=14,
            gridcolor='LightGrey',
            ticks='outside',
            showline=True,
            linecolor='black',
        ),
        plot_bgcolor='white',
        autosize=True
    )
    return fig

def plot_india_daily_recovered(cases_ts):
    fig = go.Figure(data=[go.Bar(x=cases_ts['Date'],y=cases_ts['Daily Recovered'])])
    fig.update_traces(marker_color='green')
    fig.update_layout(
        title='New Recovered Cases Over Time in India',
        font_size=10,
        xaxis_tickfont_size=14,
        xaxis=dict(
            ticks='outside',
            showline=True,
            linecolor='black',
        ),
        yaxis=dict(
            title='# of recovered cases',
            titlefont_size=14,
            tickfont_size=14,
            gridcolor='LightGrey',
            ticks='outside',
            showline=True,
            linecolor='black',
        ),

        plot_bgcolor='white',
        autosize=True
    )
    return fig

def plot_india_testing_over_time(owid_covid_data):

    data = []

    tmp = owid_covid_data[owid_covid_data['location']=="India"][['date', 'new_tests_per_thousand']]
    tmp = tmp.replace(np.nan, 0)
    tmp['new_tests_per_million'] = tmp['new_tests_per_thousand']*1000
    tmp['SMA_7'] = tmp['new_tests_per_million'].rolling(window=7).mean()
    tmp = tmp.replace(np.nan, 0)
    idxx = tmp[tmp['SMA_7'].values>0].index[0]
    tmp  = tmp.loc[idxx:,:]

    data.append(
        go.Scatter(
            x = tmp['date'][:-1],
            y = tmp['SMA_7'][:-1].astype(int),
            mode='lines+markers',
            hovertemplate="Date: %{x},<br>Daily Tests (per million): %{y}<extra></extra>",
        )
    )

    layout = go.Layout(
        title='COVID-19 tests (per mn) over time in India:<br><i style="font-size:10px">The figures are given as a rolling 7-day average.</i>',
        font_size=10,
        xaxis_tickfont_size=14,
        xaxis=dict(
            ticks='outside',
            showline=True,
            linecolor='black',
        ),
        yaxis=dict(
            tickfont_size=14,
            gridcolor='LightGrey',
            ticks='outside',
            showline=True,
            linecolor='black',
        ),
        plot_bgcolor='white', height=500,
        autosize=True,
        
    )

    fig = go.Figure(data,layout)
    fig.update_xaxes(showspikes=True)
    return fig

def plot_india_test_per_confirmed(owid_covid_data):

    tmp = owid_covid_data[owid_covid_data['location']=='India'][['date', 'new_cases', 'new_tests']]

    tmp = owid_covid_data[owid_covid_data['location']=='India'][['date', 'new_cases', 'new_tests']]
    tmp['tests_per_confirmed'] = tmp['new_tests']/tmp['new_cases']
    tmp['tpc_sw'] = tmp['tests_per_confirmed'].rolling(window=7).mean()
    idxx = tmp[tmp['tpc_sw'].values>0].index[0]
    tmp  = tmp.loc[idxx:,:]

    data = []
    data.append(
        go.Scatter(
            x = tmp['date'][:-1],
            y = tmp['tpc_sw'][:-1],
            mode='lines+markers',
            connectgaps=True,
            hovertemplate="Date: %{x},<br>Tests per Confirmed: %{y:,.2f}<extra></extra>",
        )
    )

    layout = go.Layout(
        title='Tests conducted per new confirmed cases<br><i style="font-size:10px">The figures are given as a rolling 7-day average.</i>',
        font_size=10,
        xaxis_tickfont_size=14,
        xaxis=dict(
            ticks='outside',
            showline=True,
            linecolor='black',
        ),
        yaxis=dict(
            tickfont_size=14,
            gridcolor='LightGrey',
            ticks='outside',
            showline=True,
            linecolor='black',
        ),
        plot_bgcolor='white',
        # width=900, height=600,
        autosize=True,
        
    )

    fig = go.Figure(data,layout)
    fig.update_xaxes(showspikes=True)
    return fig, tmp['tpc_sw'].iloc[-2]