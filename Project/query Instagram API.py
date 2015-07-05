# This file is exported from IPython Notebook
# Paris July Database
# Retrieving JSON data from Instagram API 

get_ipython().magic(u'matplotlib inline')
from instagram.client import InstagramAPI
from pandas import *
import pandas as pd
import numpy as np
import json
import requests
import time, datetime


# Querying Instagram API for geo-tagged media within 5km radius from the Center of Paris during July 2014 

# I: Define parameters
# 1) Time Frame
# convert dates to timestamps
startdate = datetime.datetime(2014, 7, 1, 0, 1) 
startstamp = int(time.mktime(startdate.timetuple()))
enddate = datetime.datetime(2014, 7, 31, 0, 1) 
stampstop = int(time.mktime(enddate.timetuple()))

# Query Instragram location feeds for each ten-minute interval in July 2014
interval = np.arange(startstamp,stampstop,600)
print 'time blocks:' , len(interval)

# 2) Location: the center of Paris
LAT = 48.8567
LNG = 2.3508

# II: Define functions
# Debug: If dict key does not exist, return None
def null_safe(d, key):
    try:
        return d[key]
    except:
        return None

# Pull media data (JSON format) from 5K radius from the center of Paris for each given time frame (ten-min intervals during July 2015)
def media_info(start_stamp):
    end_stamp = start_stamp + 300 # pull a call once every five minutes
    # complete url 
    url = 'https://api.instagram.com/v1/media/search?access_token=962754581.1fb234f.f3af128d5ea34a139b59afb1bec5d534&lat=%s&lng=%s&max_timestamp=%s&min_timestamp=%s&distance=5000' % (LAT, LNG,end_stamp,start_stamp)
    # retrieve data
    data = requests.get(url).text
    data = json.loads(data)['data']  # load a json string into a collection of lists and dicts
    data =  [dict(username = r['user']['username'], 
               userid = r['user']['id'],
               profilepic = r['user']['profile_picture'],
               link = r['link'],
               latitude = r['location']['latitude'],
               longitude = r['location']['longitude'],
               locId = null_safe(r['location'],'id'),
               locName = null_safe(r['location'],'name'),
               createdtime = r['created_time'],
               caption = null_safe(r['caption'],'text'),
               mediaId = r['id'],
               images = r['images']['standard_resolution']['url']
              ) for r in data]
    return data

# Fetch data (JSON format)
def fetch_instagram(interval):
    print interval
    try:
        result = pd.DataFrame(media_info(interval))
    except KeyError:
        return None
    except ValueError:
        return None
    except ConnectionError:
        return None
    return result

# Build data table
def build_table(interval):
    dfs = [fetch_instagram(r) for r in interval]
    dfs = [d for d in dfs if d is not None]
    return pd.concat(dfs, ignore_index=True)


# III: Assemble Paris Database
insta_paris = build_table(interval)
insta_paris.to_csv('insta_paris_July.csv',encoding='utf-8',index=False) 
