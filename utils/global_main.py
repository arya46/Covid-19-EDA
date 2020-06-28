import plotly.graph_objects as go

def plot_global_trend_CAD(global_deaths_trend, global_active_trend, global_confirmed_trend, all_dates):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=all_dates, y=global_deaths_trend, fill='tozeroy', \
                            name='Death Cases', line_color='red')) # fill down to xaxis
    fig.add_trace(go.Scatter(x=all_dates, y=global_active_trend, fill='tonexty', \
                            name='Active Cases', line_color='blue')) # fill to y of next trace
    fig.add_trace(go.Scatter(x=all_dates, y=global_confirmed_trend, fill='tonexty', \
                            name='Confirmed Cases', line_color='purple')) # fill to y of next trace

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
    annotations.append(dict(xref='paper', yref='paper', 
                            x=0.0, y=1.05,
                            xanchor='left', yanchor='bottom',
                            text='Global COVID-19 cases over time',
                            font=dict(family='Arial',
                                    size=14,
                                    color='rgb(37,37,37)'),
                            showarrow=False))

    fig.update_layout(annotations=annotations, plot_bgcolor='white', hovermode='x', autosize=True)
    return fig