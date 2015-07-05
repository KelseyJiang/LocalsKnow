''' This file is exported from IPython Notebook'''
# Query Foursquare API to obtain representative photos of each attraction

get_ipython().magic(u'matplotlib inline')
from instagram.client import InstagramAPI
from pandas import *
import pandas as pd
import numpy as np
import json
import requests
import time, datetime
import pymysql as mdb
from sqlalchemy import create_engine
from sqlalchemy.types import String 

# Accessing data with the pymysql driver
# Database info
username='root'
password=''
server='localhost'
databaseName='HelloParis'

# Create connection with MySQL database
engineString = 'mysql+pymysql://'+ username +':'+ password +'@'+ server +'/'+databaseName + '?charset=utf8mb4'
sqlEngine = create_engine(engineString)
con = sqlEngine.connect()

query = "Select * FROM eng_den_utm_cluster"
sqlResult = con.execute(query)
eng_den_utm_cluster = pd.DataFrame(sqlResult.fetchall())
eng_den_utm_cluster.columns = sqlResult.keys()

query = "Select * FROM fr_den_utm_cluster"
sqlResult = con.execute(query)
fr_den_utm_cluster = pd.DataFrame(sqlResult.fetchall())
fr_den_utm_cluster.columns = sqlResult.keys()

query = "Select * FROM local_den_utm_cluster"
sqlResult = con.execute(query)
local_den_utm_cluster = pd.DataFrame(sqlResult.fetchall())
local_den_utm_cluster.columns = sqlResult.keys()

def location_id(LAT,LNG):
    LAT = LAT
    LNG = LNG
    # complete url 
    url = 'https://api.foursquare.com/v2/venues/search?ll=%s,%s&oauth_token=%s' %  (LAT, LNG,token)
    # retrieve data
    data = requests.get(url).text
    data = json.loads(data)['response']['venues'][0]['id']  # load a json string into a collection of lists and dicts
    return data

# Query Foursquare API to obtain location ids
local_locid = [location_id(local_den_utm_cluster.loc[i,'loc_latitude'],local_den_utm_cluster.loc[i,'loc_longitude']) for i in range(0,local_den_utm_cluster.shape[0])]   
eng_locid = [location_id(eng_den_utm_cluster.loc[i,'loc_latitude'],eng_den_utm_cluster.loc[i,'loc_longitude']) for i in range(0,eng_den_utm_cluster.shape[0])]   
fr_locid = [location_id(fr_den_utm_cluster.loc[i,'loc_latitude'],fr_den_utm_cluster.loc[i,'loc_longitude']) for i in range(0,fr_den_utm_cluster.shape[0])]   

eng_den_utm_cluster_locid = concat([eng_den_utm_cluster, DataFrame(eng_locid)], axis=1)
fr_den_utm_cluster_locid = concat([fr_den_utm_cluster, DataFrame(fr_locid)], axis=1)
local_den_utm_cluster_locid = concat([local_den_utm_cluster, DataFrame(local_locid)], axis=1)

eng_den_utm_cluster_locid.rename(columns={eng_den_utm_cluster_locid.columns[18]:'foursquare_id'}, inplace=True)
fr_den_utm_cluster_locid.rename(columns={fr_den_utm_cluster_locid.columns[18]:'foursquare_id'}, inplace=True)
local_den_utm_cluster_locid.rename(columns={local_den_utm_cluster_locid.columns[18]:'foursquare_id'}, inplace=True)

local_den_utm_cluster_locid.to_csv('local_den_utm_cluster_locid.csv',encoding='utf-8',index=False)
fr_den_utm_cluster_locid.to_csv('fr_den_utm_cluster_locid.csv',encoding='utf-8',index=False)
eng_den_utm_cluster_locid.to_csv('eng_den_utm_cluster_locid.csv',encoding='utf-8',index=False)


# Query Foursquare API to obtain photo links
# Debug: If dict key does not exist, return None
def null_safe(d, key):
    try:
        return d[key]
    except:
        return None

def location_pic(venue_id):
    try:
        venue_id = venue_id
        # complete url 
        photourl = 'https://api.foursquare.com/v2/venues/%s/photos?oauth_token=%s' % (venue_id,token)
        # retrieve data
        photodata = requests.get(photourl).text 
        prefix = json.loads(photodata)['response']['photos']['items'][0]['prefix']
        suffix = json.loads(photodata)['response']['photos']['items'][0]['suffix']
        image_url = prefix +'width500' + suffix
    except IndexError:
        image_url = None
    except KeyError:
        image_url = None
    return image_url

local_loc_photo = [location_pic(local_den_utm_cluster_locid.loc[i,'foursquare_id']) for i in range(0,local_den_utm_cluster_locid.shape[0])] 
fr_loc_photo = [location_pic(fr_den_utm_cluster_locid.loc[i,'foursquare_id']) for i in range(0,fr_den_utm_cluster_locid.shape[0])]   
eng_loc_photo = [location_pic(eng_den_utm_cluster_locid.loc[i,'foursquare_id']) for i in range(0,eng_den_utm_cluster_locid.shape[0])] 

# Debug: for attractions with missing photo links, manually add photo links
local_loc_photo[34] = 'https://chicandgeek.files.wordpress.com/2012/07/caserne-pompiers-rousseau-rue-du-jour.jpg'
eng_loc_photo[31] = 'https://irs1.4sqi.net/img/general/600x600/38126519_iOtBBet61c_pBBh_rBaIcFXMB4pcq5gD_gvJCQ2l_iw.jpg'
eng_loc_photo[60] = 'http://www.paris-paris-paris.com/var/paris/storage/images/paris_landmarks/restaurants/french_cuisine/l_avenue/l_avenue_paris/190225-1-eng-GB/l_avenue_paris_large.jpg'
eng_loc_photo[95] = 'https://s-media-cache-ak0.pinimg.com/736x/c2/c1/ab/c2c1abd5f257f2a8aa537519fd8309bf.jpg'
eng_loc_photo[156] = 'http://www.tendaysinparis.com/wp-content/uploads/2011/09/Frenchie-Wine-Bar-Outside-2-Edited.jpg'
eng_loc_photo[177] = 'http://2.bp.blogspot.com/_c4mjx_CEFls/TJxrxyzsVSI/AAAAAAAAAAU/RrzZ2xfKJHg/s1600/IFM.jpg'

fr_loc_photo[93] = 'https://chicandgeek.files.wordpress.com/2012/07/caserne-pompiers-rousseau-rue-du-jour.jpg'
fr_loc_photo[127] = 'http://www.marjorierwilliams.com/wp-content/uploads/2012/09/DSCN3726.jpg'
fr_loc_photo[146] = 'http://viralknot.com/wp-content/uploads/2013/07/Luxembourg_Palace.jpg?d5970a'
fr_loc_photo[188] = 'http://www.djoybeat.com/wp-content/uploads/2013/02/293_photo-dehors-la-machine-moulin.jpg'


eng_den_utm_cluster_photo = concat([eng_den_utm_cluster_locid, DataFrame(eng_loc_photo)], axis=1)
fr_den_utm_cluster_photo = concat([fr_den_utm_cluster_locid, DataFrame(fr_loc_photo)], axis=1)
local_den_utm_cluster_photo = concat([local_den_utm_cluster_locid, DataFrame(local_loc_photo)], axis=1)


eng_den_utm_cluster_photo.rename(columns={eng_den_utm_cluster_photo.columns[19]:'photo'}, inplace=True)
fr_den_utm_cluster_photo.rename(columns={fr_den_utm_cluster_photo.columns[19]:'photo'}, inplace=True)
local_den_utm_cluster_photo.rename(columns={local_den_utm_cluster_photo.columns[19]:'photo'}, inplace=True)

# Export dataframes to .csv files
local_den_utm_cluster_photo.to_csv('local_den_utm_cluster_photo.csv',encoding='utf-8',index=False)
fr_den_utm_cluster_photo.to_csv('fr_den_utm_cluster_photo.csv',encoding='utf-8',index=False)
eng_den_utm_cluster_photo.to_csv('eng_den_utm_cluster_photo.csv',encoding='utf-8',index=False)

# Export dataframes to MySQL database
local_den_utm_cluster_photo.to_sql('local_den_utm_cluster_photo', sqlEngine, if_exists='replace', index=True)
fr_den_utm_cluster_photo.to_sql('fr_den_utm_cluster_photo', sqlEngine, if_exists='replace', index=True)
eng_den_utm_cluster_photo.to_sql('eng_den_utm_cluster_photo', sqlEngine, if_exists='replace', index=True)



