import requests
import pandas as pd
import numpy as np
import os
import sqlite3
from tqdm.auto import tqdm

# CONSTANT VALUES
OWNER = 'CSSEGISandData'
REPO = 'COVID-19'
PATH = 'csse_covid_19_data/csse_covid_19_daily_reports'
URL = f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}'
print(f'Downloading paths from {URL}')


download_urls = []
response = requests.get(URL)
for data in tqdm(response.json()):
    if data['name'].endswith('.csv'):
        download_urls.append(data['download_url'])


# List of labels to be renamed
relabel = {
    # 'Last Update': 'Last_Update',
    'Country/Region': 'Country_Region',
    'Lat': 'Latitude',
    'Long_': 'Longitude',
    'Province/State': 'Province_State',
}


def factor_dataframe(dat, filename):
    """ Refactor the dataframe to be uploaded into a SQL database
    as a pandas DataFrame
    """
    # rename labels
    for label in dat:
        if label in relabel:
            dat = dat.rename(columns = {label: relabel[label]})
    
    # return a dataframe with these parameters
    labels = ['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']
    # filename is datetime
    if 'Last_Update' not in dat:
        dat['Last_Update'] = pd.to_datetime(filename)

    # replace columns not in dataframe with nan
    for label in labels:
        if label not in dat:
            dat[label] = np.nan

    return dat[labels]

def upload_to_sql(filenames, db_name, debug=False):
    """ Given a list of paths, upload to a database
    """
    conn = sqlite3.connect(f"{db_name}.db")
    
    if debug:
        print("Uploading into database")
    for i, file_path in tqdm(list(enumerate(filenames))):
        
        dat = pd.read_csv(file_path)

        # rename labels
        filename = os.path.basename(file_path).split('.')[0]
        dat = factor_dataframe(dat, filename)

        # write records to sql database
        if i == 0: # if first entry, and table name already exist, replace
            dat.to_sql(db_name, con=conn, index = False, if_exists='replace')
        else: # otherwise append to current table given db_name
            dat.to_sql(db_name, con=conn, index = False, if_exists='append')


# upload into sql database
upload_to_sql(download_urls, 'example', debug=True)