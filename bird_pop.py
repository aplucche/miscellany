"""
    bird_pop.py
    ~~~~~~~~~~~
    Download and format data.gov.uk datasets for d3 visualization
    Usage::
        run in project directory - creates project directories if needed
"""

import requests
import os
import pandas as pd
import zipfile

files = {'wild_bird_populations':'https://data.gov.uk/dataset/wild_bird_populations/datapackage.zip',
    'emissions_of_air_pollutants':'https://data.gov.uk/dataset/emissions_of_air_pollutants/datapackage.zip',
    'organic_statistics_notice_uk':'https://data.gov.uk/dataset/organic_statistics_notice_uk/datapackage.zip'}

RAW_DATA_DIRECTORY = './raw_data'
TRANSFORMED_DATA_DIRECTORY = './transformed_data'

def download_files_if_needed(url,name):
    filepath = os.path.join(RAW_DATA_DIRECTORY,name+'.zip')
    if os.path.isfile(filepath):
        return
    print 'downloading {} from {}'.format(name, url)
    r = requests.get(url)
    with open(filepath, "wb") as f:
        f.write(r.content)
    return

###
#Project Setup
###
#Create project directories if needed
if not os.path.exists('./raw_data'):
    os.makedirs('./raw_data')
if not os.path.exists('./transformed_data'):
    os.makedirs('./transformed_data')

#Download Files if needed
for k,v in files.iteritems():
    download_files_if_needed(v,k)

###
#Process Wild Bird Populations
###
z = zipfile.ZipFile(os.path.join(RAW_DATA_DIRECTORY,'wild_bird_populations'+'.zip'))
bp_df = pd.read_csv(z.open('data/uk_birds_2015d.csv'))

#remove unneeded columns and rename
columns_used = [('year',0),('all_species',1)] #(name, column position)
bp_df = bp_df[[bp_df.columns[column[1]] for column in columns_used]] 
bp_df.columns = [column[0] for column in columns_used]

###
#Process Emissions of Air Pollutants
###
z = zipfile.ZipFile(os.path.join(RAW_DATA_DIRECTORY,'emissions_of_air_pollutants'+'.zip'))
ap_df = pd.read_csv(z.open('data/website_trends-air-emissions_2013.csv'))

#remove unneeded columns and rename
columns_used = [('year',0),('Ammonia Index',2),
                ('Nitrogen Oxides Index',4),('Sulphur Dioxide Index',6),
                ('Non-Methane Volatile Organic Compounds Index',8),
                ('pm10 Index',10),('pm2.5 Index',12)] #(name, column position)
ap_df = ap_df[[ap_df.columns[column[1]] for column in columns_used]] 
ap_df.columns = [column[0] for column in columns_used]

###
#Join Datasets on Year and Export
###
export_df = pd.merge(bp_df, ap_df, on='year', how='outer')
export_df = export_df.fillna('')
export_df.to_csv(os.path.join(TRANSFORMED_DATA_DIRECTORY,'visualization_data.csv'), index=False)