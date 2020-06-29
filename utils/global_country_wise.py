import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import math

def plot_countries_chloropeth(df_global):

    customdata = pd.Series(
        data='Death: ' + df_global['deaths'].astype(str) + '<br>' +\
            'Recovered: ' + df_global['recovered'].astype(str) + '<br>' +\
            'Active: ' + df_global['active'].astype(str)
        )

    fig = go.Figure(data=go.Choropleth(

        locations = df_global['Country/Region'],
        locationmode='country names',
        z = df_global['confirmed'],
        text = df_global['Country/Region'],
        colorscale = px.colors.sequential.Plasma,
        customdata=customdata,
        
        hovertemplate="<b>%{text}</b><br><br>" +
                        "Confirmed %{z:,.0f}<br>" +
                        "%{customdata}<br>" +
                        "<extra></extra>",
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_title = 'Confirmed<br>Cases',
    ))

    fig.update_layout(
        autosize=True,
        height=700,  
    )
        

    return fig

def plot_country_wise_latest_cases(df, num_top_countries, all_dates, label):
        
    df_temp = df.sort_values(all_dates[-1], ascending= False)[:num_top_countries]
    df_temp.replace('United Kingdom', 'UK', inplace=True)
    df_temp.replace('Saudi Arabia', 'U.A.E.', inplace=True)

    colour = {
        'Confirmed': 'purple',
        'Death': 'red',
        'Recovered': 'green',
        'Active': 'orange'
    }
    
    # plt.figure(figsize=(20,15))
    plt.axes(axisbelow=True)
    plt.bar(df_temp["Country/Region"],\
            df_temp[all_dates[-1]],
            color=colour[label])
    plt.xticks(rotation=50)
    plt.yticks(ticks=[500000, 1000000, 1500000, 2000000, 2500000], labels=['5 Lakhs', '10 Lakhs', '15 Lakhs', '20 Lakhs', '25 Lakhs'])
    plt.ylabel("# of {} cases".format(label))
    plt.grid(alpha=0.3)
    plt.tight_layout()
    return plt

def plot_country_wise_trend(df, trend_key, num_top_countries, all_dates, label):

    tmp = df.sort_values(all_dates[-1], ascending= False)[:num_top_countries]
    
    fig = make_subplots(rows=math.ceil(tmp.shape[0]/2), cols=2,
                        horizontal_spacing=0.25, 
                        subplot_titles=tmp['Country/Region'].values)
    
    if(trend_key == 'Cumulative'):
        for idx, country in enumerate(list(tmp['Country/Region'])):
        
            fig.add_trace(go.Scatter(x = all_dates,y = tmp.iloc[idx][all_dates],
                                     mode='lines',
                                     name = country,
                                     hovertemplate="Date: %{x},<br>"+
                                                   "Total Cases: %{y}" +
                                                   "<extra></extra>",
                                    ),
                          row=math.ceil((idx+1)/2), 
                          col=math.ceil((idx%2)+1))


            # Update xaxis properties
            fig.update_xaxes(row=math.ceil((idx+1)/2), 
                             col=math.ceil((idx%2)+1), 
                             showline=True, linecolor='black',
                             showspikes=True)

            # Update yaxis properties
            fig.update_yaxes(row=math.ceil((idx+1)/2), 
                             col=math.ceil((idx%2)+1), 
                             gridcolor='LightGrey',ticks='outside', showline=True, linecolor='black')
        
    elif(trend_key == 'Daily New Cases'):
        for idx, country in enumerate(list(tmp['Country/Region'])):

            pqr = tmp.iloc[idx][all_dates].diff()
            pqr.iloc[0] = tmp.iloc[idx][all_dates].iloc[0]
            
            fig.add_trace(go.Bar(x = all_dates,
                                 y = pqr,
                                 name = country,
                                 hovertemplate="Date: %{x},<br>"+
                                               "New Cases: %{y}" +
                                               "<extra></extra>",
                                ),
                          row=math.ceil((idx+1)/2), 
                          col=math.ceil((idx%2)+1))


            # Update xaxis properties
            fig.update_xaxes(row=math.ceil((idx+1)/2), 
                             col=math.ceil((idx%2)+1), 
                             showline=True, linecolor='black')

            # Update yaxis properties
            fig.update_yaxes(row=math.ceil((idx+1)/2), 
                             col=math.ceil((idx%2)+1), 
                             gridcolor='LightGrey',ticks='outside', showline=True, linecolor='black')

    # Update title and height
    fig.update_layout(height=math.ceil(tmp.shape[0]/2)*300, 
                        autosize=True, showlegend=False,
                        font_size=12,
                        title_text="Countrywise {} Cases: {} (Top {})".format(trend_key, label, num_top_countries))


    fig.update_layout(
        plot_bgcolor='white',
    )

    return fig
        
def plot_country_wise_bending_curve_are(owid_covid_data, compare_countries):

    data = []


    for country in compare_countries:
        tmp  = owid_covid_data[owid_covid_data['location']==country][['date', 'new_cases', 'total_cases']]

        customdata = pd.Series(
            data="Country: <b>" + str(country) + "</b><br>Daily New Cases: " + tmp['new_cases'].astype(str) + "<br>Total Cases: " + tmp['total_cases'].astype(str) + "<br>"
        )
        data.append(
            go.Scatter(
                x = np.log10(tmp['total_cases']),
                y = np.log10(tmp['new_cases']),
                mode='lines',
                name = country,
                text = tmp['date'],
                customdata=customdata,
                hovertemplate="%{customdata}" + 
                                    "Date: %{text}<br>"+
                                        "<extra></extra>",
                ),

            )
    layout = go.Layout(
        title='Daily vs. Total confirmed COVID-19 cases: <br><i style="font-size:12px">Shown is the 7-day rolling average of confirmed cases.</i>',
        xaxis_tickfont_size=14,
        xaxis=dict(
            title='Total confirmed cases',
            ticks='outside',
            showline=True,
            linecolor='black',
            tickmode = 'array',
            tickvals = [0, 1, 2, 3, 4, 5, 6],
            ticktext = ['1', '10', '100', '1,000', '10,000', '1,00,000', '1 M']
        ),
        yaxis=dict(
            title='Daily confirmed cases',
            tickfont_size=14,
            gridcolor='LightGrey',
            ticks='outside',
            showline=True,
            linecolor='black',
            tickmode = 'array',
            tickvals = [0, 1, 2, 3, 4, 5, 6],
            ticktext = ['1', '10', '100', '1,000', '10,000', '1,00,000', '1 M']
        
        ),
        plot_bgcolor='white',
        autosize=True,
        showlegend=False
    )

    fig = go.Figure(data,layout)

    return fig

def plot_country_wise_bending_curve_when(owid_covid_data, compare_countries):

    fig = make_subplots(rows=math.ceil(len(compare_countries)/2), cols=2, 
                    subplot_titles=compare_countries,)
                    # horizontal_spacing = ,
                    # vertical_spacing = 0.04)

    for idx, country in enumerate(compare_countries):

        tmp  = owid_covid_data[owid_covid_data['location']==country][['new_cases', 'date']]
        tmp['SMA_7'] = tmp['new_cases'].rolling(window=7).mean()
        tmp = tmp.replace(np.nan, 0)
        idxx = tmp[tmp['SMA_7'].values>=30].index[0]
        tmp  = tmp.loc[idxx:,:]

        fig.add_trace(go.Scatter(x = list(range(tmp.shape[0])),
                                    y = tmp['SMA_7'].astype(int),
                                    mode='lines',
                                    name = country,
                                    hovertemplate="Day %{x:,.0f},<br>"+
                                                    "Number of new confirmed cases = %{y}" +
                                                    "<extra></extra>",
                                ),
                        row=math.ceil((idx+1)/2), 
                        col=math.ceil((idx%2)+1))


        # Update xaxis properties
        fig.update_xaxes(row=math.ceil((idx+1)/2), 
                            col=math.ceil((idx%2)+1), 
                            title='Days since confirmed cases first reached 30 per day',
                            titlefont=dict(size=11),
                            showline=True, linecolor='black',
                            showspikes=True)

        # Update yaxis properties
        fig.update_yaxes(row=math.ceil((idx+1)/2), 
                            col=math.ceil((idx%2)+1),
                            gridcolor='LightGrey',ticks='outside', showline=True, linecolor='black')
            
    # Update title and height
    fig.update_layout(height=math.ceil(len(compare_countries)/2)*350, 
                    autosize=True, showlegend=False,
                    plot_bgcolor='white',
                    title_text='Daily confirmed cases:<br><i style="font-size:12px">Shown is the 7-day rolling average of confirmed cases.</i>',
                    )

    fig.update_layout(margin=dict(t=150))
        
    return fig
