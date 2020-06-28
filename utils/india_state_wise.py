import folium
from folium.plugins import MarkerCluster
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt


def plot_india_state_wise_cases(state_key, trend_key, covidIN_state_wise_daily):
    """
    Filters and plot the dataframe as a stacked distribution plot of count 'Confirmed', 
    'Recovered' and 'Deceased'.

    Args:
    -----
        * state_key (str): the state to filter on
        * trend_key      : display cumulative / daily plots

        Note: the dataframe to plot is globally defined here as `df`

    Returns:
    --------
        A plotly chart

    """
    tmp = covidIN_state_wise_daily[['Date', 'Status'] + list([state_key])]
    # tmp = tmp.replace(np.nan,  0)
    tmp.loc[tmp[state_key] < 0, state_key] = 0
    
    date      = tmp[tmp['Status'] == 'Confirmed']['Date'].reset_index(drop=True)
    confirmed = tmp[tmp['Status'] == 'Confirmed'][state_key].reset_index(drop=True)
    recovered = tmp[tmp['Status'] == 'Recovered'][state_key].reset_index(drop=True)
    deceased  = tmp[tmp['Status'] == 'Deceased'][state_key].reset_index(drop=True)

    fig = make_subplots(rows=3, cols=1, 
                        vertical_spacing=0.20,
                        subplot_titles=("Confirmed","Recovered", "Deaths"))

    if(trend_key == 'Cumulative'):

        fig.add_trace(go.Scatter(x = date,
                                 y = np.cumsum(confirmed),
                                 mode='lines+markers',
                                 name = 'Confirmed',
                                 text = None,
                                 marker_color='indianred'),
                     row=1, col=1)
        fig.add_trace(go.Scatter(x = date,
                                 y = np.cumsum(recovered),
                                 mode='lines+markers',
                                 name = 'Recovered',
                                 text = None,
                                 marker_color='green'),
                     row=2, col=1)
        fig.add_trace(go.Scatter(x = date,
                                 y = np.cumsum(deceased),
                                 mode='lines+markers',
                                 name = 'Deceased',
                                 text = None,
                                 marker_color='grey'),
                     row=3, col=1)
       
    elif(trend_key == 'Daily New Cases'):
    
        fig.add_trace(go.Bar(x=date, 
                             y=confirmed,
                             name='Confirmed',
                             marker_color='indianred'),
                      row=1, col=1)
        fig.add_trace(go.Bar(x=date, 
                             y=recovered,
                             name='Recovered',
                             marker_color='green'
                            ),
                      row=2, col=1)
        fig.add_trace(go.Bar(x=date, 
                             y=deceased,
                             name='Deceased',
                             marker_color='grey'
                            ),
                      row=3, col=1)
    
    # Update xaxis properties
    fig.update_xaxes(row=1, col=1, showline=True, linecolor='black')
    fig.update_xaxes(row=2, col=1, showline=True, linecolor='black')
    fig.update_xaxes(row=3, col=1, showline=True, linecolor='black')

    # Update yaxis properties
    fig.update_yaxes(row=1, col=1, gridcolor='LightGrey',ticks='outside', showline=True, linecolor='black')
    fig.update_yaxes(row=2, col=1, gridcolor='LightGrey',ticks='outside', showline=True, linecolor='black') 
    fig.update_yaxes(row=3, col=1, gridcolor='LightGrey',ticks='outside', showline=True, linecolor='black')
    
    fig.update_layout(
        plot_bgcolor='white',
    )
    
    fig.add_layout_image()

    # Update title and height
    fig.update_layout(height=3*300, showlegend=False, autosize=True,
                      title_text="StateWise Spread Trend: {}".format(trend_key.upper()))
    
    return fig

def plot_india_state_wise_contribution(num_state_to_display, covidIN_state_wise):
    num_state_to_display = num_state_to_display + 1
    tmp = covidIN_state_wise[['State', 'Confirmed']]
    tmp['Percent'] = tmp['Confirmed']/tmp.iloc[0,1]*100
    tmp.drop(tmp[tmp['State'] == 'State Unassigned'].index, 
            inplace=True)
    tmp = tmp.sort_values(['Percent'], ascending=False).reset_index(drop=True)
    tmp = tmp.append({'State' : 'Other States and UTs' , 
                    'Confirmed' : tmp['Confirmed'][num_state_to_display:].sum(), 
                    'Percent' : tmp['Percent'][num_state_to_display:].sum()}, 
                    ignore_index=True)
    tmp = tmp.drop(tmp.index[num_state_to_display:-1]).reset_index(drop=True)

    yrange = np.arange(tmp.shape[0])

    fig, ax = plt.subplots()

    plt.hlines(y = yrange, xmin = 0, xmax = tmp['Percent'], color='#3590ae', alpha=0.6, linewidth = 5)
    plt.plot(tmp['Percent'], yrange, "o", markersize = 7, color='black', alpha=0.6)

    # add annotations
    for i in range(tmp.shape[0]):
            plt.text((tmp.iloc[i][2])+2, i, 
                    str(np.round(tmp.iloc[i][2], 2)) + '%  (' + str(tmp.iloc[i][1]) + ')', color='black', 
                    fontsize = 9, va = 'center', ha = 'left')

    # Plot Formatting
    ax.set_title('StateWise Contributions', 
                fontsize=12,
                pad = 10)
                
    ax.set_xlabel('Percent Contribution', fontsize = 10)
        
    ax.set_yticks(yrange)
    ax.set_yticklabels(tmp['State'], fontsize = 7)
    ax.invert_yaxis()

    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    return fig

def plot_india_state_wise_districts(covidIN_districtwise_current, state_key):

    tmp = covidIN_districtwise_current[covidIN_districtwise_current['State'] == state_key]\
            [['District', 'Confirmed', 'Recovered', 'Deceased', 'Active']]

    tmp.sort_values('Confirmed', inplace=True, ascending=False)
    tmp.replace('Unknown', 'Uncategorized Cases', inplace=True)

    template = f'<div class="cards">'
  
    if tmp.shape[0] > 0:
        for idx in range(tmp.shape[0]):
            template += f'<div class="card">\
                            <h3 class="dis-data-name">{tmp.iloc[idx, 0]}</h3>\
                            <div class="dis-data">\
                                <h4 class="confirmed" style="text-align: right;">{tmp.iloc[idx, 1]}</h4>\
                                <h4 class="recovered" style="text-align: left;">{tmp.iloc[idx, 2]}</h4>\
                                <h4 class="deceased" style="text-align: right;">{tmp.iloc[idx, 3]}</h4>\
                                <h4 class="active" style="text-align: left;">{tmp.iloc[idx, 4]}</h4>\
                            </div>\
                        </div>'
        template += '</div>'
        return template
    else:
        return f'No district wise data available for <b>{state_key}.<b>'
        


# def plot_india_state_wise_chloropeth(df_state_map):
#     state_map= folium.Map(tiles="CartoDBpositron", location=[22.9734,78.6569], zoom_start=5, max_zoom=6, min_zoom=5)

#     #for each coordinate, create circlemarker
#     for i in range(df_state_map.shape[0]):

#             lat = df_state_map.iloc[i]['lat']
#             longs = df_state_map.iloc[i]['lon']
#             tooltip = "<span style='font-weight: bold'>State : {} </span><br>" + "Confirmed : {} <br>" + "State : {} <br>" + "Confirmed : {} <br>" + "State : {} <br>"

#             tooltip = tooltip.format(df_state_map.iloc[i]['st_nm'],
#                                     df_state_map.iloc[i]['confirmed'],
#                                     df_state_map.iloc[i]['active'],
#                                     df_state_map.iloc[i]['recovered'],
#                                     df_state_map.iloc[i]['deaths'])
            
#             radius=int(np.log2(df_state_map.iloc[i]['confirmed']+1))+2,

#             folium.CircleMarker(location = [lat, longs], radius=radius, tooltip=tooltip, fill=True).add_to(state_map)

#     return state_map