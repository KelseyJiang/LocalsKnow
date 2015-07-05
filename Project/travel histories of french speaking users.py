# This file is exported from IPython Notebook
get_ipython().magic(u'matplotlib inline')
from sqlalchemy import *
import pandas as pd
import requests
import time, datetime
import numpy as np
import json
from geopy.distance import great_circle

sns.set_context('talk')
sns.set_style('darkgrid') 
plt.rcParams['figure.figsize'] = 12, 8  # plotsize 

# Accessing data with the pymysql driver
username='root'
password=''
server='localhost'
databaseName='HelloParis'
tableName='GPS_language'

#Create connection with MySQL database
engineString = 'mysql+pymysql://'+ username +':'+ password +'@'+ server +'/'+databaseName + '?charset=utf8mb4'
sqlEngine = create_engine(engineString)

con = sqlEngine.connect()

query = "Select * FROM paris_lang_loc WHERE prob > 0.95 AND loc_name NOT IN ('Paris','Paris, France','DROP') AND language = 'fr'"
sqlResult = con.execute(query)
fr_lang_loc = pd.DataFrame(sqlResult.fetchall())
fr_lang_loc.columns = sqlResult.keys()

# Drop duplicated users in any given sites
fr_lang_loc = fr_lang_loc.drop_duplicates(subset=['userid','loc_name'])
user_list = fr_lang_loc['userid']


# Time Frame
# Convert dates to timestamps
startdate = datetime.datetime(2014, 1, 1, 0, 1) 
startstamp = int(time.mktime(startdate.timetuple()))
enddate = datetime.datetime(2014, 5, 30, 0, 1) 
stampstop = int(time.mktime(enddate.timetuple()))
interval = np.arange(startstamp,stampstop,2592000 )

# Debug: If dict key does not exist, return None
def null_safe(d, key):
    try:
        return d[key]
    except:
        return None

# For all french speaking users in the database, obtain the first documented location in Jan, Feb and March 2014
def user_info(start_stamp, userid):
    end_stamp = start_stamp + 2592000 
    url = 'https://api.instagram.com/v1/users/%s/media/recent?access_token=962754581.1fb234f.f3af128d5ea34a139b59afb1bec5d534&min_timestamp=%s&max_timestamp=%s' % (userid,start_stamp,end_stamp)
    data_raw = requests.get(url).text
    try:
        data_extract = json.loads(data_raw)['data'][1]
        data_entry = [dict(userid = null_safe(data_extract['user'],'id'),
                  mediaId = null_safe(data_extract,'id'),
                  latitude = null_safe(data_extract['location'],'latitude'),
                  longitude = null_safe(data_extract['location'],'longitude'),
                  caption = null_safe(data_extract['caption'],'text'),
                  images = data_extract['images']['standard_resolution']['url'],
                  locId = null_safe(data_extract['location'],'id'),
                  locName = null_safe(data_extract['location'],'name'),
                  createdtime = null_safe(data_extract,'created_time'),
                  start_stamp = start_stamp
                 )]
    except IndexError:
        data_entry = [dict(userid = userid,
                  mediaId = None,
                  latitude = None,
                  longitude = None,
                  caption = None,
                  images = None,
                  locId = None,
                  locName = None,
                  createdtime = None,
                  start_stamp = start_stamp
                 )]
    return data_entry


def strip_id(x):
    result = str(x)
    result = result.strip('.')[0]
    return result


# Fetch data
def fetch_instagram(interval, userid):
    print interval
    try:
        result = pd.DataFrame(user_info(interval,userid))
    except KeyError:
        return None
    except ValueError:
        return None
    except ConnectionError:
        return None
    return result

# Build table
def build_table(interval, userid):
    dfs = [fetch_instagram(interval, int(float(i))) for i in userid]
    dfs = [d for d in dfs if d is not None]
    return pd.concat(dfs, ignore_index=True)

# Schedule tasks so that the number of requests per hour does not exceed Instagram API limit
# Randominze pausing time 
def timed_exe(interval,user_list):
    start_time = time.time()
    table = build_table(interval,user_list)
    end_time = time.time()
    timediff = end_time - start_time
    if timediff < 3600:
        print start_time,end_time,timediff,np.random.randint(timediff,timediff+10, size=1)[0]
        time.sleep(np.random.randint(3600-timediff,3700-timediff, size=1)[0])
        return table
    else:
        return table


# Assemble user travel history database; export as csv file; store db in MySQL database
user_history_Jan = {}
user_history_Jan['interval_%s'% 0] = timed_exe(interval[0],user_list)   
user_history_Jan_df = pd.concat(user_history_Jan,ignore_index=True)
user_history_Jan_df.to_csv('user_history_Jan_df.csv',encoding='utf-8',index=False)
user_history_Jan_df.to_sql('user_history_Jan_df', sqlEngine, if_exists='replace', index=True)


user_history_feb = {}
user_history_feb['interval_%s'% 1] = timed_exe(interval[1],user_list) #user_list[0:4500] per hour    
user_history_feb_df = pd.concat(user_history_feb,ignore_index=True)
user_history_feb_df.to_csv('user_history_feb_df.csv',encoding='utf-8',index=False)
user_history_feb_df.to_sql('user_history_feb_df', sqlEngine, if_exists='replace', index=True)

user_history_mar = {}
user_history_mar['interval_%s'% 2] = timed_exe(interval[2],user_list) #user_list[0:4500] per hour    
user_history_mar_df = pd.concat(user_history_mar,ignore_index=True)
user_history_mar_df.to_csv('user_history_mar_df.csv',encoding='utf-8',index=False)
user_history_mar_df.to_sql('user_history_mar_df', sqlEngine, if_exists='replace', index=True)

history_Jan_df = user_history_Jan_df.dropna(subset=['latitude']).reset_index(drop = True)
history_feb_df = user_history_feb_df.dropna(subset=['latitude']).reset_index(drop = True)
history_mar_df = user_history_mar_df.dropna(subset=['latitude']).reset_index(drop = True)


all_history = history_Jan_df.append(history_feb_df,ignore_index=True).append(history_mar_df,ignore_index=True)
all_history = history_Jan_df.append(history_feb_df,ignore_index=True).append(history_mar_df,ignore_index=True)

# Calculate the great circle distance between each French speaking user's first logged location in Jan/Feb/Mar to the center of Paris
# If the user were present at Paris, tagged as "local"; otherwise, tagged as "informed" (to be distinguished from presumably less informed English speaking "visitors" in Paris)
subset = all_history[['latitude', 'longitude']]
loc_tuples = [tuple(x) for x in subset.values]
all_history['dist'] = [great_circle(loc, paris).miles for loc in loc_tuples]
all_user_history = all_history[['userid','dist']].groupby(['userid'], as_index=False)['dist'].min().sort(['dist'], ascending=False).reset_index(drop=True)
all_user_history['group'] = 'informed'
all_user_history.loc[all_user_history['dist']<20,'group'] = 'local'
all_user_history.to_sql('all_user_history', sqlEngine, if_exists='replace', index=True)

con.close()





