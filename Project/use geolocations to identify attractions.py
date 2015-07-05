''' This file is exported from IPython Notebook'''
# Use geo-location tags to identify the corresponding attractions
get_ipython().magic(u'matplotlib inline')
import pymysql as mdb
from sqlalchemy import create_engine
from sqlalchemy.types import String 
from pandas import *
import pandas as pd
import re
import numpy as np
import json
import requests
import time, datetime

# Load instagram API data
paris_csv = pd.read_csv('insta_paris_July_lan.csv',encoding='utf-8') 
paris_csv = paris_csv.drop_duplicates().reset_index(drop = True)
paris_csv = paris_csv.rename(columns = {'0':'language','1': 'prob'})

# Remove entries that do not come with GPS coordinates or userid
paris_csv = paris_csv[np.logical_and(pd.notnull(paris_csv['longitude']) , pd.notnull(paris_csv['latitude']))].reset_index(drop = True)
paris_csv = paris_csv[pd.notnull(paris_csv['userid'])].reset_index(drop = True)
paris_csv = paris_csv[np.logical_and(pd.notnull(paris_csv['language']) , pd.notnull(paris_csv['prob']))].reset_index(drop = True)
paris_csv['longitude'] = [float(paris_csv['longitude'][i]) for i in range(0,paris_csv.shape[0])]

# Database cleaning: remove GPS coordinates outside of paris
paris_csv = paris_csv.loc[np.logical_and(paris_csv['latitude'] < 48.92, paris_csv['latitude'] > 48.80),:].reset_index(drop = True)
paris_csv = paris_csv.loc[np.logical_and(paris_csv['longitude'] < 2.4370, paris_csv['longitude'] > 2.2297),:].reset_index(drop = True)

# Debug: If dict key does not exist, return None
def null_safe(d, key):
    try:
        return d[key]
    except:
        return None

# For all geo-coordinates in the database, identify the name of the attraction and the location Id
def loc_info(latitude, longitude): 
    url = 'https://api.instagram.com/v1/locations/search?access_token=962754581.1fb234f.f3af128d5ea34a139b59afb1bec5d534&lat=%s&lng=%s' % (latitude, longitude)
    # retrieve data
    data_raw = requests.get(url).text
    try:
        data_extract = json.loads(data_raw)['data'][1]
        data_entry = [dict(loc_latitude = null_safe(data_extract,'latitude'),
                  loc_longitude = null_safe(data_extract,'longitude'),
                  loc_name = null_safe(data_extract,'name'),
                  loc_id = null_safe(data_extract,'id'),
                  ori_latitude =  str(latitude),
                  ori_longitude = str(longitude)    
                 )]
    except IndexError:
        data_entry = [dict(loc_latitude = None,
                  loc_longitude = None,
                  loc_name = None,
                  loc_id = None,
                  ori_latitude =  str(latitude),
                  ori_longitude = str(longitude)    
                 )]
    return data_entry

# 
def loc_fetch(latitude, longitude): 
    print latitude, longitude
    try:
        result = pd.DataFrame(loc_info(latitude, longitude))
    except KeyError:
        return None
    except ValueError:
        return None
    except ConnectionError:
        return None
    return result

# Build data table
def build_table(data):
    #dfs = [loc_fetch(data['latitude'][i], data['longitude'][i]) for i in range(0,10)]
    dfs = [loc_fetch(data['latitude'][i], data['longitude'][i]) for i in range(0, data.shape[0])]
    dfs = [d for d in dfs if d is not None]
    return pd.concat(dfs, ignore_index=True)

# Schedule tasks so that the number of requests per hour does not exceed Instagram API limit
# Randominze pause time 
def timed_exe(data):
    start_time = time.time()
    table = build_table(data)
    end_time = time.time()
    timediff = end_time - start_time
    if timediff < 3600:
        print start_time,end_time,timediff,np.random.randint(timediff,timediff+10, size=1)[0]
        time.sleep(np.random.randint(3650-timediff,3700-timediff, size=1)[0])
        #time.sleep(np.random.randint(1,10, size=1)[0])
        return table
    else:
        return table


loc_id_nm_4800 = timed_exe(paris_csv[0:4800])
loc_id_nm_9600 = timed_exe(paris_csv[4800:9600].reset_index(drop = True)) 
loc_id_nm_14400 = timed_exe(paris_csv[9600:14400].reset_index(drop = True))
loc_id_nm_19200 = timed_exe(paris_csv[14400:19200].reset_index(drop = True))
loc_id_nm_24005 = timed_exe(paris_csv[19200:24005].reset_index(drop = True)) 
loc_id_nm_24908 = timed_exe(paris_csv[24005:24908].reset_index(drop = True)) 

all_loc = pd.concat([loc_id_nm_4800,loc_id_nm_9600,loc_id_nm_14400,loc_id_nm_19200,loc_id_nm_24005,loc_id_nm_24908],ignore_index = True)
paris_lang_loc = pd.concat([paris_csv, all_loc], axis=1)


# Export as .csv file
paris_lang_loc.to_csv('paris_lang_loc.csv',encoding='utf-8',index=False)


# Save dataframe to MySQL Database
engine = create_engine("mysql+pymysql://root:@localhost/HelloParis?charset=utf8mb4") 
paris_lang_loc.to_sql('paris_lang_loc', engine, if_exists='replace', index=True)
