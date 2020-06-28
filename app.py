import streamlit as st
import os
import requests
from datetime import datetime 
import time
import math
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np


from utils.global_main import plot_global_trend_CAD
from utils.global_country_wise import plot_countries_chloropeth, plot_country_wise_latest_cases, plot_country_wise_trend
from utils.global_country_wise import plot_country_wise_bending_curve_are, plot_country_wise_bending_curve_when     
from utils.india_main import plot_india_trend_CAD, plot_india_daily_confirmed, plot_india_daily_deaths, plot_india_daily_recovered
from utils.india_main import plot_india_testing_over_time, plot_india_test_per_confirmed
# from utils.india_state_wise import plot_india_state_wise_chloropeth
from utils.india_state_wise import plot_india_state_wise_cases, plot_india_state_wise_contribution, plot_india_state_wise_districts
from utils.india_states_dict import states_lat_long, states_mapper, states_helpline, get_helpline_no


PATH = 'data'

# get_data
@st.cache(show_spinner=False)
def load_all_datas(PATH):

    df_confirmed = pd.read_csv(os.path.join(PATH, 'df_confirmed.csv'))
    df_deaths = pd.read_csv(os.path.join(PATH, 'df_deaths.csv'))
    df_recovered = pd.read_csv(os.path.join(PATH, 'df_recovered.csv'))

    owid_covid_data = pd.read_csv(os.path.join(PATH, 'owid_covid_data.csv'))

    cases_ts = pd.read_csv(os.path.join(PATH, 'cases_ts.csv'))
    covidIN_statewise_test = pd.read_csv(os.path.join(PATH, 'covidIN_statewise_test.csv'))
    covidIN_state_wise = pd.read_csv(os.path.join(PATH, 'covidIN_state_wise.csv'))
    covidIN_state_wise_daily = pd.read_csv(os.path.join(PATH, 'covidIN_state_wise_daily.csv'))
    covidIN_districtwise_current = pd.read_csv(os.path.join(PATH, 'covidIN_districtwise_current.csv'))

    df_confirmed = df_confirmed.replace(np.nan, '', regex=True)
    df_deaths = df_deaths.replace(np.nan, '', regex=True)
    df_recovered = df_recovered.replace(np.nan, '', regex=True)

    ignore_col = ['Province/State', 'Country/Region', 'Lat', 'Long']
    all_dates = list(set(df_confirmed.columns) - set(ignore_col))
    all_dates.sort(key = lambda date: datetime.strptime(date, "%m/%d/%y"))

    return df_confirmed, df_deaths, df_recovered, \
        owid_covid_data, cases_ts, covidIN_statewise_test, \
            covidIN_state_wise, covidIN_state_wise_daily, \
                covidIN_districtwise_current, all_dates

@st.cache(show_spinner=False)
def global_focus_load_data(df_confirmed, df_deaths, df_recovered, all_dates):
        df_global_confirmed = df_confirmed.groupby(['Country/Region'])[all_dates[-1]].sum()
        df_global_deaths    = df_deaths.groupby(['Country/Region'])[all_dates[-1]].sum()
        df_global_recovered = df_recovered.groupby(['Country/Region'])[all_dates[-1]].sum()

        df_global = pd.DataFrame({
            'confirmed': df_global_confirmed,
            'deaths'   : df_global_deaths,
            'recovered': df_global_recovered
        }).reset_index()

        df_global['active'] = df_global['confirmed'] - (df_global['deaths'] + df_global['recovered'])
        df_global['mortality_rate (per 100)'] = np.round(100 * df_global['deaths'] / df_global['confirmed'], 2)

        df_global.replace('US', "USA", inplace=True)
        df_global.replace('Korea, South', 'South Korea', inplace=True)
        df_global.replace('Taiwan*', "Taiwan", inplace=True)
        df_global.replace('Reunion', "Réunion", inplace=True)
        df_global.replace('Gambia, The', "Gambia", inplace=True)
        df_global.replace("Cote d'Ivoire", "Côte d'Ivoire", inplace=True)
        df_global.replace('Congo (Brazzaville)', "Republic of the Congo", inplace=True)
        df_global.replace('Congo (Kinshasa)', "Democratic Republic of the Congo", inplace=True)
        df_global.replace('Bahamas, The', "Bahamas", inplace=True)

        return df_global

@st.cache(show_spinner=False)
def countrywise_focus_load_data(df_confirmed, df_deaths, df_recovered, all_dates):
        df_confirmed_countrywise = df_confirmed.groupby(['Country/Region'])[all_dates].sum().reset_index()
        df_deaths_countrywise    = df_deaths.groupby(['Country/Region'])[all_dates].sum().reset_index()
        df_recovered_countrywise = df_recovered.groupby(['Country/Region'])[all_dates].sum().reset_index()

        df_active_countrywise = df_confirmed_countrywise[all_dates] - (df_deaths_countrywise[all_dates] + df_recovered_countrywise[all_dates])
        df_active_countrywise.set_index(df_confirmed_countrywise['Country/Region'], inplace=True)
        df_active_countrywise.reset_index(inplace=True)

        return df_confirmed_countrywise, df_deaths_countrywise, \
            df_recovered_countrywise, df_active_countrywise

# @st.cache(show_spinner=False)
# def india_state_chloropeth_load_data(states_lat_long, covidIN_state_wise):
#     df_state_chloropeth = pd.DataFrame(columns=['st_nm', 'lat', 'lon', 'confirmed', 'deaths', 'recovered', 'active'])
#     for state in list(states_lat_long.keys()):
#         df_state_chloropeth = df_state_chloropeth.append(
#             {
#                 'st_nm' : state , 
#                 'lat' : states_lat_long[state][0], 
#                 'lon' : states_lat_long[state][1],
#                 'confirmed': covidIN_state_wise[covidIN_state_wise['State'].str.contains(state)]['Confirmed'].values[0],
#                 'deaths': covidIN_state_wise[covidIN_state_wise['State'].str.contains(state)]['Deaths'].values[0],
#                 'recovered': covidIN_state_wise[covidIN_state_wise['State'].str.contains(state)]['Recovered'].values[0],
#                 'active': covidIN_state_wise[covidIN_state_wise['State'].str.contains(state)]['Active'].values[0],
#             }, 
#             ignore_index=True)    
#     return df_state_chloropeth

# Streamlit encourages well-structured code, like starting execution in a main() function.
def main(): 

    df_confirmed, df_deaths, df_recovered, \
        owid_covid_data, cases_ts, covidIN_statewise_test, \
            covidIN_state_wise, covidIN_state_wise_daily, covidIN_districtwise_current, \
                all_dates  = load_all_datas(PATH)
    

    st.sidebar.title("Menu")
    app_mode = st.sidebar.radio("", ["Home", "Country Wise Analysis", "India Focus", "Indian States", \
        "COVID-19 Guide", "About the app"], index=0)

    if app_mode == "Home":

        df_global = global_focus_load_data(df_confirmed, df_deaths, df_recovered, all_dates)

        st.title('COVID-19 Analysis and Visualization')
        st.markdown("<hr style='margin: 0'>", unsafe_allow_html=True)

        st.image('static/img/corona-header.png', use_column_width=True)

        st.write('Coronaviruses are a large family of viruses which may cause illness in animals or humans. \
            In humans, several coronaviruses are known to cause respiratory infections ranging from the common \
                cold to more severe diseases such as **Middle East Respiratory Syndrome (MERS)** and **Severe Acute \
                    Respiratory Syndrome (SARS)**. The most recently discovered coronavirus causes coronavirus disease \
                        **COVID-19**. This new virus and disease were unknown before the outbreak began in Wuhan, China, \
                            in December 2019. Due to its high rate spreads throughout the world, **WHO** declared it as a Public \
                                Health Emergency of International Concern (ie. pandemic) on 30 January 2020.')
        st.write('*To know more, go the **COVID-19 Guide** section*.')

        st.write(f'As of {datetime.strptime(all_dates[-1], "%m/%d/%y").strftime("%d %b %Y")}, the number of cases across the world are:')

        # ------------------ global dashboard starts here ------------------#
        st.markdown('<style>' + open('static/css/custom_css.css').read() + '</style>', unsafe_allow_html=True)
        global_cases = f'<div><div class="head-data-cards">\
                        <div class="head-data-card confirmed">\
                            <h4 class="">Confirmed</h4>\
                            <h2 class="case-number">{df_global["confirmed"].sum()}</h2>\
                        </div>\
                        <div class="head-data-card deceased">\
                            <h4 class="" >Deaths</h4>\
                            <h2 class="case-number">{df_global["deaths"].sum()}</h2>\
                        </div>\
                        <div class="head-data-card recovered">\
                            <h4 class="" >Recovered</h4>\
                            <h2 class="case-number">{df_global["recovered"].sum()}</h2>\
                        </div>\
                        <div class="head-data-card active">\
                            <h4 class="" >Active</h4>\
                            <h2 class="case-number">{df_global["active"].sum()}</h2>\
                        </div>'
        global_cases += '</div></div>'
        st.markdown(global_cases, unsafe_allow_html=True)
        # ------------------ global dashboard starts here ------------------#

        # ------------------ global trends starts here ------------------#
        global_confirmed_trend = df_confirmed[all_dates].sum(axis=0)
        global_deaths_trend    = df_deaths[all_dates].sum(axis=0)
        global_recovered_trend = df_recovered[all_dates].sum(axis=0)

        global_active_trend = pd.Series(
            data=np.array(
                [x1 - x2 - x3  for (x1, x2, x3) in zip(global_confirmed_trend.values,\
                                                    global_deaths_trend.values, \
                                                    global_recovered_trend.values)]),
            index=global_confirmed_trend.index
        )

        st.write('    ')
        st.write('Lets look at how the cases are growing over time:')
        st.plotly_chart(plot_global_trend_CAD(global_deaths_trend, global_active_trend, global_confirmed_trend, all_dates),
                        use_container_width=True)
        # ------------------ global trend ends here ------------------#
        st.write("The curve is increasing everyday. Since, there is no drug available to cure this disease yet, we\
            should take appropriate precautions to prevent ourselves from the risks of getting infected with the virus.")

        st.image('static/img/corona-preventions.jpg', use_column_width=True)

    elif app_mode == "Country Wise Analysis":

        df_global = global_focus_load_data(df_confirmed, df_deaths, df_recovered, all_dates)
        df_confirmed_countrywise, \
            df_deaths_countrywise, \
                df_recovered_countrywise, \
                    df_active_countrywise = countrywise_focus_load_data(df_confirmed, df_deaths, df_recovered, all_dates)

        st.title("COVID-19: Country Wise")
        st.markdown("<hr style='margin: 0'>", unsafe_allow_html=True)

        st.write("Let's look at how the virus has spread across different countries:")

        # ------------------ chloropeth starts here ------------------#
        st.plotly_chart(plot_countries_chloropeth(df_global), use_container_width=True)
        # ------------------ chloropeth ends here ------------------#

        # ------------------ confirmed cases starts here ------------------#
        st.header("Countries with most number CONFIRMED cases:")

        num_top_countries1a = st.slider('Number of countries to display: ', 4, 16, 10, 1, key='confa')
        st.pyplot(plot_country_wise_latest_cases(df_confirmed_countrywise, num_top_countries1a, all_dates, 'Confirmed'), clear_figure=True)
     
        st.markdown('<h3 style="font-weight:400">The cases over time:</h3>', unsafe_allow_html=True)

        trend_key1 = st.selectbox("Trend", ["Cumulative", "Daily New Cases"], key='confb')
        num_top_countries1b = st.slider('Number of countries to display: ', 4, 16, 8, 1, key='confc')
        st.plotly_chart(plot_country_wise_trend(df_confirmed_countrywise, trend_key1, num_top_countries1b, all_dates, 'Confirmed'),
                        use_container_width=True)

        # ------------------ confirmed cases ends here ------------------#

        # ------------------ death cases starts here ------------------#
        st.header("Countries with most number DEATH cases:")

        num_top_countries2a = st.slider('Number of countries to display: ', 4, 16, 8, 1, key='deatha')
        st.pyplot(plot_country_wise_latest_cases(df_deaths_countrywise, num_top_countries2a, all_dates, 'Death'), clear_figure=True)
     
        st.markdown('<h3 style="font-weight:400">The cases over time:</h3>', unsafe_allow_html=True)

        trend_key2 = st.selectbox("Trend", ["Cumulative", "Daily New Cases"], key='deathb')
        num_top_countries2b = st.slider('Number of countries to display: ', 4, 16, 8, 1, key='deathc')
        st.plotly_chart(plot_country_wise_trend(df_deaths_countrywise, trend_key2, num_top_countries2b, all_dates, 'Deaths'),
                        use_container_width=True)
        # ------------------ death cases ends here ------------------#

        # ------------------ recovered cases starts here ------------------#
        st.header("Countries with most number RECOVERY cases:")

        num_top_countries3a = st.slider('Number of countries to display: ', 4, 16, 8, 1, key='recova')
        st.pyplot(plot_country_wise_latest_cases(df_recovered_countrywise, num_top_countries3a, all_dates, 'Recovered'), clear_figure=True)
     
        st.markdown('<h3 style="font-weight:400">The cases over time:</h3>', unsafe_allow_html=True)

        trend_key3 = st.selectbox("Trend", ["Cumulative", "Daily New Cases"], key='recovb')
        num_top_countries3b = st.slider('Number of countries to display: ', 4, 16, 8, 1, key='recovc')
        st.plotly_chart(plot_country_wise_trend(df_recovered_countrywise, trend_key3, num_top_countries3b, all_dates, 'Recovered'),
                        use_container_width=True)
        # ------------------ recovered cases starts here ------------------#


        # ------------------ active cases starts here ------------------#
        st.header("Countries with most number ACTIVE cases:")

        num_top_countries4a = st.slider('Number of countries to display: ', 4, 16, 8, 1, key='activea')
        st.pyplot(plot_country_wise_latest_cases(df_active_countrywise, num_top_countries4a, all_dates, 'Confirmed'), clear_figure=True)
     
        st.markdown('<h3 style="font-weight:400">The cases over time:</h3>', unsafe_allow_html=True)

        trend_key4 = st.selectbox("Trend", ["Cumulative", "Daily New Cases"], key='activeb')
        num_top_countries4b = st.slider('Number of countries to display: ', 4, 16, 8, 1, key='activec')
        st.plotly_chart(plot_country_wise_trend(df_active_countrywise, trend_key4, num_top_countries4b, all_dates, 'ACTIVE'),
                        use_container_width=True)
        # ------------------ active cases ends here ------------------#

        # ------------------ bend the curve: ARE? starts here ------------------#
        st.header("Are the countries able to bend the curve?")
   
        compare_countries = ['United States', 'Canada', 'Spain', 'India', 'Peru',\
            'France', 'Germany', 'Brazil', 'Russia', 'Chile', 'Iran',\
                'Pakistan', 'Mexico', 'United Kingdom', 'New Zealand', 'Italy',\
                    'Turkey']

        selected_countries1 = st.multiselect('Select Countries', compare_countries, \
            ['United States', 'Spain', 'India', 'Germany', 'Russia', 'Pakistan', 'United Kingdom', 'New Zealand', 'Brazil'],
                key='sel_country1')

        st.plotly_chart(plot_country_wise_bending_curve_are(owid_covid_data, selected_countries1), use_container_width=True)

        st.write('- Countries like Germany, UK, Spain, New Zealand, Canada, Italy, France have been able to bend the curve. \
            The number of new confirmed cases is decreasing day by day.')

        st.write("- Countries like USA, India, Russia, Pakistan, Brazil, Mexico aren't still able to bend the curve yet. The number\
            of new confirmed cases is increasing everyday in these countries.")
        # ------------------ bend the curve: ARE? ends here ------------------#

        # ------------------ bend the curve: WHEN? starts here ------------------#
        st.header("When did countries bend the curve?")

        selected_countries2 = st.multiselect('Select Countries', compare_countries, \
            ['United States', 'Spain', 'India', 'Germany', 'Russia', 'Pakistan', 'United Kingdom', 'New Zealand'],\
                key='sel_country2')
        st.plotly_chart(plot_country_wise_bending_curve_when(owid_covid_data, selected_countries2), use_container_width=True)

        st.write('- Countries like Germany, UK, Spain have been able to bend the curve very early. It took around 30-60 days\
            to bend the curve (from the day on which first 30 confirmed cases were found) in these countries.')
        st.write('- Due to strict government policies, the virus did not spread much in New Zealand. They are already\
            successful in containing the virus.')
        st.write("- India is proving to be a failure in handling the COVID-19. The number of new confirmed cases is increasing\
            day by day. The country have not reached its peak yet. The rising number of cases can be attributed to the fact that,\
                unlike other countries, the GoI re-opened the lockdown even before reaching the peak.")
        # ------------------ bend the curve: WHEN? ends here ------------------#

    elif app_mode == "India Focus":
        
        st.title("Coronavirus Outbreak in India")
        st.markdown("<hr style='margin: 0'>", unsafe_allow_html=True)

        tmp = df_confirmed.groupby(['Country/Region'])[all_dates[-1]].sum().sort_values(ascending=False).reset_index()
        tmp = tmp[tmp['Country/Region'] == 'India'].index.values[0]

        st.write(f'As of {datetime.strptime(all_dates[-1], "%m/%d/%y").strftime("%d %b %Y")}, India is at number **{tmp+1}** in terms of \
            total confirmed cases.')

        st.markdown('<style>' + open('static/css/custom_css.css').read() + '</style>', unsafe_allow_html=True)
        india_overall = f'<div><div class="head-data-cards">\
                        <div class="head-data-card confirmed">\
                            <h4 class="">Confirmed</h4>\
                            <h2 class="case-number">{covidIN_state_wise.iloc[0]["Confirmed"]}</h2>\
                        </div>\
                        <div class="head-data-card deceased">\
                            <h4 class="" >Deaths</h4>\
                            <h2 class="case-number">{covidIN_state_wise.iloc[0]["Deaths"]}</h2>\
                        </div>\
                        <div class="head-data-card recovered">\
                            <h4 class="" >Recovered</h4>\
                            <h2 class="case-number">{covidIN_state_wise.iloc[0]["Recovered"]}</h2>\
                        </div>\
                        <div class="head-data-card active">\
                            <h4 class="" >Active</h4>\
                            <h2 class="case-number">{covidIN_state_wise.iloc[0]["Active"]}</h2>\
                        </div>'
        india_overall += '</div></div>'
        st.markdown(india_overall, unsafe_allow_html=True)


        # ------------------ india all cases trend starts here ------------------#
        st.write('    ')
        st.header("Spread of COVID-19 cases in India over time:")
        st.plotly_chart(plot_india_trend_CAD(cases_ts), use_container_width=True)
        # ------------------ india all cases trend ends here ------------------#

        st.markdown("<h3 style='font-weight:400'>Let's look at the daily cases:</h3>", unsafe_allow_html=True)
        # ------------------ daily confirmed cases starts here ------------------#
        st.plotly_chart(plot_india_daily_confirmed(cases_ts), use_container_width=True)
        # ------------------ daily confirmed ends here ------------------#

        # ------------------ daily deaths cases starts here ------------------#
        st.plotly_chart(plot_india_daily_deaths(cases_ts), use_container_width=True)
        # ------------------ daily deaths ends here ------------------#

        # ------------------ daily recovered cases starts here ------------------#
        st.plotly_chart(plot_india_daily_recovered(cases_ts), use_container_width=True)
        # ------------------ daily recovered ends here ------------------#

        # ------------------ testing in India starts here ------------------#
        st.header('Are we testing enough?')
        st.plotly_chart(plot_india_testing_over_time(owid_covid_data), use_container_width=True)
        # ------------------ testing in India ends here ------------------#

        # ------------------ testing effectivestarts here ------------------#
        st.header('How effective are these tests?')
        chart, tpc_num = plot_india_test_per_confirmed(owid_covid_data)
        st.plotly_chart(chart, use_container_width=True)
        st.write(f'As the number of testing has increased, the **"tests conducted per new confirmed"** \
            rate is decreasing every other day. This means that the chances of a test being positive is increasing.')

        st.write(f'As of **{datetime.strptime(all_dates[-1], "%m/%d/%y").strftime("%d %b %Y")}**, a new case is confirmed after\
            testing **{int(tpc_num)}** samples.')
        # ------------------ testing effective ends here ------------------#

        # st.header('Are we in par with other countries? (TODO)')
        # st.write('Will be updated soon!')

    elif app_mode == "Indian States":
  
        st.title("Coronavirus Outbreak in India: State Wise")
        st.markdown("<hr style='margin: 0'>", unsafe_allow_html=True)

        # ------------------ india state wise chloropeth trend starts here ------------------#
        # df_state_chloropeth = india_state_chloropeth_load_data(states_lat_long, covidIN_state_wise)
        # statewise_chloropeth = plot_india_state_wise_chloropeth(df_state_chloropeth)

        # st.markdown(statewise_chloropeth, unsafe_allow_html=True)
        # ------------------ india state wise chloropeth ends here ------------------#

        # ------------------ india state wise trend starts here ------------------#
        st.markdown("<h3 style='font-weight:400'>Let's look at how COVID-19 cases has spread in different\
             states over time:</h3>", unsafe_allow_html=True)

        def state_label_mapper(key):
            return states_mapper[key]

        state_key = st.selectbox('State', list(states_mapper.keys()), index=3, format_func=state_label_mapper, key='state_contrib')
        trend_key_sw = st.selectbox("Trend", ["Cumulative", "Daily New Cases"], key='trend_key_sw')

        st.plotly_chart(plot_india_state_wise_cases(state_key, trend_key_sw, covidIN_state_wise_daily), use_container_width=True)
        # ------------------ india state wise trend ends here ------------------#

        # ------------------ india state wise contribution starts here ------------------#
        num_state_to_display = st.slider("Select top number of states:", min_value=6, max_value=15, value=6, step=1, key='state_contrib')
        st.pyplot(plot_india_state_wise_contribution(num_state_to_display, covidIN_state_wise))
        # ------------------ india state wise contribution ends here ------------------#

        # ------------------ india district wise cases starts here ------------------#
        st.markdown("<h3 style='font-weight:400'>Current districtwise cases for each state:</h3>", unsafe_allow_html=True)

        st.markdown('<style>' + open('static/css/custom_css.css').read() + '</style>', unsafe_allow_html=True)
        state_key2 = st.selectbox('State', list(states_mapper.values()), index=3, key='district_wise')
        district_data = plot_india_state_wise_districts(covidIN_districtwise_current, state_key2)

        legend_text = '<div class="legends">\
                            <p style="color: #dc3545; font-weight: 800; font-size: 13px;">CONFIRMED</p>\
                            <p style="color: #28a745; font-weight: 800; font-size: 13px;">RECOVERED</p>\
                            <p style="color: #6c757d; font-weight: 800; font-size: 13px;">DEATHS</p>\
                            <p style="color: #007bff; font-weight: 800; font-size: 13px;">ACTIVE</p>\
                        </div>'
        st.markdown(legend_text, unsafe_allow_html=True)
        st.markdown(district_data, unsafe_allow_html=True)
        # ------------------ india district wise cases ends here ------------------#
    
    elif app_mode == "COVID-19 Guide":
        st.markdown('<style>' + open('static/css/custom_css.css').read() + '</style>', unsafe_allow_html=True)
        st.title("COVID-19 Guide")
        st.markdown("<hr style='margin: 0'>", unsafe_allow_html=True)

        st.markdown("<h3 style='font-weight:600; text-align:center;'>Coronavirus Symptoms</h3>", unsafe_allow_html=True)
        symptoms = f'<div class="Eb8Pib">\
                        <div class="gVDAsd">\
                            <div class="Eq0l7e">\
                                <img alt="Fever" src="https://www.gstatic.com/healthricherkp/covidsymptoms/light_fever.gif" height="55px" width="55px">\
                            </div>\
                            <div class="EdNVSd">Fever</div>\
                        </div>\
                        <div class="gVDAsd">\
                            <div class="Eq0l7e">\
                                <img alt="Dry cough" src="https://www.gstatic.com/healthricherkp/covidsymptoms/light_cough.gif" height="55px" width="55px">\
                            </div>\
                            <div class="EdNVSd">Dry cough</div>\
                        </div>\
                        <div class="gVDAsd">\
                            <div class="Eq0l7e">\
                                <img alt="Tiredness" src="https://www.gstatic.com/healthricherkp/covidsymptoms/light_tiredness.gif" height="55px" width="55px">\
                            </div>\
                            <div class="EdNVSd">Tiredness</div>\
                        </div>\
                    </div>'
        st.markdown(symptoms, unsafe_allow_html=True)
        st.write('COVID-19 affects different people in different ways. Most infected people will develop mild to moderate illness and \
            recover without hospitalization.')
        st.markdown('<p>Most common symptoms:</p>\
                    <ul>\
                        <li>fever</li><li>dry cough</li><li>tiredness</li>\
                    </ul>', unsafe_allow_html=True)
        st.markdown('<p>Serious symptoms:</p>\
                    <ul>\
                        <li>difficulty breathing or shortness of breath</li>\
                        <li>chest pain or pressure</li>\
                        <li>loss of speech or movement</li>\
                    </ul>', unsafe_allow_html=True)
        st.markdown('<p>Less common symptoms:</p>\
                    <ul>\
                        <li>aches and pains</li>\
                        <li>sore throat</li>\
                        <li>diarrhoea</li>\
                        <li>conjunctivitis</li>\
                        <li>headache</li>\
                        <li>loss of taste or smell</li>\
                        <li>a rash on skin, or discolouration of fingers or toes</li>\
                    </ul>', unsafe_allow_html=True)
        
        st.markdown("<h3 style='font-weight:600; text-align:center;'>Coronavirus Treatments</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-weight:500;'>To date, there are no specific vaccines or medicines for COVID-19. Treatments are under investigation, \
            and will be tested through clinical trials.</p>", unsafe_allow_html=True)
        st.markdown("<p>Self-care:<br>If you feel sick you should rest, drink plenty of fluid, and eat nutritious food. Stay\
             in a separate room from other family members, and use a dedicated bathroom if possible. Clean and disinfect\
                  frequently touched surfaces.<br>\
                Everyone should keep a healthy lifestyle at home. Maintain a healthy diet,\
                   sleep, stay active, and make social contact with loved ones through the phone or internet. Children need\
                        extra love and attention from adults during difficult times. Keep to regular routines and schedules \
                            as much as possible.<br>\
                It is normal to feel sad, stressed, or confused during a crisis. Talking to people you trust,\
                    such as friends and family, can help. If you feel overwhelmed, talk to a health worker or counsellor.</p>", unsafe_allow_html=True)
        st.markdown("<p>Medical treatments:<br>\
            If you have mild symptoms and are otherwise healthy, self-isolate and contact your medical provider or a \
                COVID-19 information line for advice. Seek medical care if you have a fever, a cough, and difficulty breathing.\
                    Call in advance.</p>", unsafe_allow_html=True)

        state_key3 = st.selectbox('State Helpline Number:', list(states_helpline.keys()), index=3, key='state_helpline')
        call_button = f'<div class="row" style="justify-content:center;">\
                <img src="https://library.kissclipart.com/20180904/fcq/kissclipart-black-call-icon-png-clipart-computer-icons-24870da4075b1930.jpg" height="30px"  style="margin-top:0.7em;">\
                <a href="tel:{get_helpline_no(state_key3, states_helpline)}" style="padding:5px; font-size: 25px;">{get_helpline_no(state_key3, states_helpline)}</a>\
            </div>'
        st.markdown(call_button, unsafe_allow_html=True)

        st.markdown("<h3 style='font-weight:600; text-align:center;'>Coronavirus Prevention</h3>", unsafe_allow_html=True)
        st.markdown('<p>Protect yourself and others around you by knowing the facts and taking appropriate precautions. \
            Follow advice provided by your local public health agency.</p>', unsafe_allow_html=True)
        st.markdown('<p>To prevent the spread of COVID-19:</p>\
                    <ul>\
                        <li>Clean your hands often. Use soap and water, or an alcohol-based hand rub.</li>\
                        <li>Maintain a safe distance from anyone who is coughing or sneezing.</li>\
                        <li>Don’t touch your eyes, nose or mouth.</li>\
                        <li>Cover your nose and mouth with your bent elbow or a tissue when you cough or sneeze.</li>\
                        <li>Stay home if you feel unwell.</li>\
                        <li>If you have a fever, cough and difficulty breathing, seek medical attention. Call in advance.</li>\
                        <li>Follow the directions of your local health authority.</li>\
                    </ul>', unsafe_allow_html=True)
        st.markdown('<p>Avoiding unneeded visits to medical facilities allows healthcare systems to operate more \
            effectively, therefore protecting you and others.</p>', unsafe_allow_html=True)

        more_info = f'<div class="f3ZnDf">\
            <a href="https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public" class="KRQ2Ab" role="button" ping="/url?sa=t&amp;source=web&amp;rct=j&amp;url=https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public&amp;ved=2ahUKEwiOwPP6oqPqAhUh7XMBHYMXDTwQz0AoCjAEegQICBAL">\
                <span class="C8rbpf">\
                    <svg focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"></path></svg>\
                </span>\
                <span class="HRfe0e">Learn more on who.int</span>\
            </a></div>'
        st.markdown(more_info, unsafe_allow_html=True)
        
    elif app_mode == "About the app":
        st.markdown('<style>' + open('static/css/custom_css.css').read() + '</style>', unsafe_allow_html=True)
        st.title("About the app")
        st.markdown("<hr style='margin: 0'>", unsafe_allow_html=True)
        st.write("This app is an extensive interactive exploratory data analysis of the spread trend of the COVID-19 virus all \
            over the world, specially India.")
        st.markdown("<p>The numbers and graphs are automatically updated at <i><b>05:00 IST</b></i> everyday.<br>\
            As such, conclusions to charts have been omitted wherever necessary to keep the app relevant.<p>", unsafe_allow_html=True)
        st.write('The app is best viewed on a desktop browser.')
        st.markdown("<h3 style='font-weight:400;'>Data Sources:</h3>\
                    <ul><li>https://ourworldindata.org/</li>\
                        <li>https://www.covid19india.org/</li>\
                    </ul>", unsafe_allow_html=True)

        st.markdown("<h3 style='font-weight:400;'>About Me: Tulrose Deori</h3>\
                    <ul><li><a href='https://arya46.github.io/'>Portfolio</a></li>\
                        <li><a href='https://github.com/arya46'>Github</a></li>\
                        <li><a href='https://www.linkedin.com/in/tulrose/'>LinkedIn</a></li>\
                    </ul>", unsafe_allow_html=True)
  
if __name__ == "__main__":
    main()
