from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from download import download
import os

PATH = 'data'

def download_files():

    print('Downloading Files:')

    df_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    df_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
    df_recovered = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

    owid_covid_data = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'

    cases_ts = 'https://api.covid19india.org/csv/latest/case_time_series.csv'
    covidIN_statewise_test = 'https://api.covid19india.org/csv/latest/statewise_tested_numbers_data.csv'
    covidIN_state_wise = 'https://api.covid19india.org/csv/latest/state_wise.csv'
    covidIN_state_wise_daily = 'https://api.covid19india.org/csv/latest/state_wise_daily.csv'
    covidIN_districtwise_current = 'https://api.covid19india.org/csv/latest/district_wise.csv'

    download(df_confirmed, os.path.join(PATH, 'df_confirmed.csv'), replace=True)
    download(df_deaths, os.path.join(PATH, 'df_deaths.csv'), replace=True)
    download(df_recovered, os.path.join(PATH, 'df_recovered.csv'), replace=True)

    download(owid_covid_data, os.path.join(PATH, 'owid_covid_data.csv'), replace=True)

    download(cases_ts, os.path.join(PATH, 'cases_ts.csv'), replace=True)
    download(covidIN_statewise_test, os.path.join(PATH, 'covidIN_statewise_test.csv'), replace=True)
    download(covidIN_state_wise, os.path.join(PATH, 'covidIN_state_wise.csv'), replace=True)
    download(covidIN_state_wise_daily, os.path.join(PATH, 'covidIN_state_wise_daily.csv'), replace=True)
    download(covidIN_districtwise_current, os.path.join(PATH, 'covidIN_districtwise_current.csv'), replace=True)

    print('Downloading Files Complete.')

sched = BackgroundScheduler()

# @sched.scheduled_job('cron', day_of_week='mon-sun', hour=00)
# @sched.scheduled_job('interval', seconds=120)
# def timed_job():
#     print('This job is run every three minutes.')

sched.add_job(download_files, 'cron', day_of_week='mon-sun', hour=5)
sched.start()