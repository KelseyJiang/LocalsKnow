''' This file is exported from IPython Notebook'''
get_ipython().magic(u'matplotlib inline')
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sqlalchemy.types import String 
from unidecode import unidecode
from pyproj import Proj
from sklearn.cluster import DBSCAN
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
sns.set_context('talk')
sns.set_style('darkgrid') 
plt.rcParams['figure.figsize'] = 12, 8  # plotsize 

# Import Data From MySQL Database
# Access data with the pymysql driver
username='root'
password=''
server='localhost'
databaseName='HelloParis'

#Create connection with MySQL database
engineString = 'mysql+pymysql://'+ username +':'+ password +'@'+ server +'/'+databaseName + '?charset=utf8mb4'
sqlEngine = create_engine(engineString)
con = sqlEngine.connect()

# Query MySQL database. Extract all attractions visited by English speakers, count the number of English speakers at each attraction and rank by counts
query = "Select loc_id, loc_name, loc_latitude,loc_longitude, COUNT(loc_name) AS eng_count FROM paris_lang_loc_local WHERE prob > 0.95 AND language = 'en' AND loc_name NOT IN ('Paris','Paris, France','DROP') GROUP BY loc_name ORDER BY eng_count DESC"
sqlResult = con.execute(query)
july_eng_freq = pd.DataFrame(sqlResult.fetchall())
july_eng_freq.columns = sqlResult.keys()

# Extract all attractions visited by French speakers, count the number of French speakers at each attraction and rank by counts
query = "Select loc_id, loc_name,loc_latitude,loc_longitude, COUNT(loc_name) AS fr_count FROM paris_lang_loc_local WHERE prob > 0.95 AND language = 'fr' AND loc_name NOT IN ('Paris','Paris, France','DROP') GROUP BY loc_name ORDER BY fr_count DESC"
sqlResult = con.execute(query)
july_fr_freq = pd.DataFrame(sqlResult.fetchall())
july_fr_freq.columns = sqlResult.keys()

# Extract all attractions visited by local Parisians, count the number of locals at each attraction and rank by counts
query = "Select loc_id, loc_name,COUNT(loc_name) AS local_count FROM paris_lang_loc_local WHERE prob > 0.95 AND user_group = 'local' AND loc_name NOT IN ('Paris','Paris, France','DROP') GROUP BY loc_name ORDER BY local_count DESC"
sqlResult = con.execute(query)
july_local_freq = pd.DataFrame(sqlResult.fetchall())
july_local_freq.columns = sqlResult.keys()

# Extract all attractions, count the number of total visitors at each attraction and rank by counts
query = "Select loc_id,loc_latitude,loc_longitude,loc_name, COUNT(loc_name) AS total_count FROM paris_lang_loc_local WHERE prob > 0.95 AND loc_name NOT IN ('Paris','Paris, France','DROP') GROUP BY loc_id ORDER BY COUNT(loc_name) DESC"
sqlResult = con.execute(query)
july_freq = pd.DataFrame(sqlResult.fetchall())
july_freq.columns = sqlResult.keys()

# Assemble the database. A large fraction of the attractions in the database were only visited by few Instagram users. Thus, for each of the three user groups (English speaker, French speaker, Locals), apply DBSCAN on top 200 visited attractions by that group.
result = pd.merge(july_fr_freq, july_eng_freq.drop('loc_id',axis=1), how='outer', on=['loc_latitude','loc_longitude','loc_name'])
result = result.fillna(0)
result2 = pd.concat([result]).groupby(['loc_name','loc_latitude','loc_longitude'], as_index=False).sum().sort('fr_count',ascending = False).reset_index(drop=True)
result3 = result2.drop(['loc_latitude', 'loc_longitude'],axis = 1).groupby(['loc_name'], as_index=False).sum().sort('fr_count',ascending = False).reset_index(drop=True)
result3 = pd.merge(result3, july_local_freq.drop('loc_id',axis=1), how='left', on=['loc_name'])
result3 = result3.fillna(0)
result4 = result2.drop(['fr_count','eng_count','loc_id'],axis = 1)
result5 = pd.merge(result3, result4, on='loc_name')
result5 = result5.fillna(0)
Top_loc = pd.concat([july_freq]).groupby(['loc_name'], as_index=False)['total_count'].sum().sort(['total_count'], ascending=False).reset_index(drop=True)[0:500]
julydf = pd.merge(Top_loc, result5, how='left', on=['loc_name'])
julydf = julydf.fillna(0)
julydf = julydf.drop_duplicates(subset = ['loc_name']).reset_index(drop = True)
tot_visitors = sum(julydf.total_count)
tot_eng_visitors = sum(julydf.eng_count)
tot_fr_visitors = sum(julydf.fr_count )
tot_local_visitors = sum(julydf.local_count)
julydf['eng_favorite'] = julydf.eng_count / tot_eng_visitors
julydf['fr_favorite'] = julydf.fr_count / tot_fr_visitors
julydf['local_favorite'] = julydf.local_count  / tot_local_visitors
julydf['all_favorite'] = julydf.total_count  / tot_visitors
julydf['fr_minus_eng'] = (julydf.fr_count  - julydf.eng_count) /julydf.total_count 

# top 200 visited attractions by English speakers
eng_top_200 = julydf.sort('eng_favorite',ascending = False)[0:200].reset_index(drop= True)
# top 200 visited attractions by French speakers
fr_top_200 = julydf.sort('fr_favorite',ascending = False)[0:200].reset_index(drop= True)
# top 200 visited attractions by locals
local_top_200 = julydf.sort('local_favorite',ascending = False)[0:200].reset_index(drop= True)


'''
DBSCAN parameters:
EPS (the maximum distance between two attractions for them to be considered as in the same neighborhood) 
EPS was set to be 0.20 (on the actual map, it corresponds to 300 meters, the distance that can be reached by 4 mins casual walking) for all three groups
MINSAMPLE  (The number of samples in a neighborhood for a point to be considered as a core point, including the point itself)
MINSAMPLE for English speaking visitors, French speaking visitors and locals are scaled to the total number of visitors in each group;
MINSAMPLE for English speaking visitors = 0.8% total English Speakers
MINSAMPLE for French speaking visitors = 0.8% total French Speakers
MINSAMPLE for Locals = 0.8% total locals

GPS coordinates were converted to UTM coordinates for DBSCAN in order to minimize spatial distortion 
'''
EPS = 0.20 
MINSAMPLE = 80

# I: DBSCAN of attractions favored by locals
local_den = local_top_200.reset_index()
local_den['local_count'] = [int(local_den.local_count[i]) for i in range(0,len(local_den.local_count))]
local_den['local_count_adjusted'] = [int(round(local_den.local_favorite[i]*10000)) for i in range(0,len(local_den.local_favorite))]
local_den2 = local_den.loc[np.repeat(local_den.index.values,local_den.local_count_adjusted)].reset_index()

# Convert GPS coordinates to UTM coordinates
myProj = Proj("+proj=utm +zone=31U, +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
UTMx, UTMy = myProj(local_den2['loc_longitude'].values, local_den2['loc_latitude'].values)
local_den_utm = local_den2
local_den_utm['UTMx']=UTMx
local_den_utm['UTMy']=UTMy

# Generate sample data
X = local_den_utm[['UTMx','UTMy']].values.tolist()
X = StandardScaler().fit_transform(X)

# Compute DBSCAN
db = DBSCAN(eps=EPS, min_samples=MINSAMPLE).fit(X) 

core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print('Estimated number of clusters: %d' % n_clusters_)

# Plot result
# Black removed and is used for noise instead
unique_labels = set(labels)
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = 'k'

    class_member_mask = (labels == k)

    xy = X[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=14)

    xy = X[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()

local_den_utm['cluster'] = labels
local_den_utm_cluster = local_den_utm.drop_duplicates()
del local_den_utm_cluster['level_0']
del local_den_utm_cluster['index']
local_den_utm_cluster = local_den_utm_cluster.reset_index()
del local_den_utm_cluster['index']


# II: DBSCAN of attractions favored by French speakers
fr_den = fr_top_200.reset_index()
fr_den['fr_count'] = [int(fr_den.fr_count[i]) for i in range(0,len(fr_den.fr_count))]
fr_den['fr_count_adjusted'] = [int(round(fr_den.fr_favorite[i]*10000)) for i in range(0,len(fr_den.fr_favorite))]
fr_den2 = fr_den.loc[np.repeat(fr_den.index.values,fr_den.fr_count_adjusted)].reset_index()

# Convert GPS coordinates to UTM coordinates
myProj = Proj("+proj=utm +zone=31U, +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
UTMx, UTMy = myProj(fr_den2['loc_longitude'].values, fr_den2['loc_latitude'].values)
fr_den_utm = fr_den2
fr_den_utm['UTMx']=UTMx
fr_den_utm['UTMy']=UTMy

# Generate sample data
X = fr_den_utm[['UTMx','UTMy']].values.tolist()
X = StandardScaler().fit_transform(X)

# Compute DBSCAN
db = DBSCAN(eps=EPS, min_samples=MINSAMPLE).fit(X) 

core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
print('Estimated number of clusters: %d' % n_clusters_)

# Plot result
# Black removed and is used for noise instead
unique_labels = set(labels)
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = 'k'

    class_member_mask = (labels == k)

    xy = X[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=14)

    xy = X[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()

fr_den_utm['cluster'] = labels
fr_den_utm_cluster = fr_den_utm.drop_duplicates()
del fr_den_utm_cluster['level_0']
del fr_den_utm_cluster['index']
fr_den_utm_cluster = fr_den_utm_cluster.reset_index()
del fr_den_utm_cluster['index']


# III: DBSCAN of attractions favored by English speakers
eng_den = eng_top_200.reset_index()
eng_den['eng_count'] = [int(eng_den.eng_count[i]) for i in range(0,len(eng_den.eng_count))]
eng_den['eng_count_adjusted'] = [int(round(eng_den.eng_favorite[i]*10000)) for i in range(0,len(eng_den.eng_favorite))]
eng_den2 = eng_den.loc[np.repeat(eng_den.index.values,eng_den.eng_count_adjusted)].reset_index()

# Convert GPS coordinates to UTM coordinates
UTMx, UTMy = myProj(eng_den2['loc_longitude'].values, eng_den2['loc_latitude'].values)
eng_den_utm = eng_den2
eng_den_utm['UTMx']=UTMx
eng_den_utm['UTMy']=UTMy

# Generate sample data
X = eng_den_utm[['UTMx','UTMy']].values.tolist()
X = StandardScaler().fit_transform(X)

# Compute DBSCAN
db = DBSCAN(eps=EPS, min_samples=MINSAMPLE).fit(X) 
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

# Number of clusters in labels, ignoring noise if present
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
print('Estimated number of clusters: %d' % n_clusters_)


# Plot result
# Black removed and is used for noise instead
unique_labels = set(labels)
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise
        col = 'k'

    class_member_mask = (labels == k)

    xy = X[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=14)

    xy = X[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()

eng_den_utm['cluster'] = labels
eng_den_utm_cluster = eng_den_utm.drop_duplicates()
del eng_den_utm_cluster['level_0']
del eng_den_utm_cluster['index']
eng_den_utm_cluster = eng_den_utm_cluster.reset_index()
eng_den_utm_cluster = eng_den_utm_cluster.drop(eng_den_utm_cluster.index[94]).reset_index(drop=True)
del eng_den_utm_cluster['index']

# Export clustering results to CSV
eng_den_utm_cluster.to_csv('eng_den_utm_cluster.csv',encoding='utf-8',index=False)
fr_den_utm_cluster.to_csv('fr_den_utm_cluster.csv',encoding='utf-8',index=False)
local_den_utm_cluster.to_csv('local_den_utm_cluster.csv',encoding='utf-8',index=False)

# Export clustering results to MySQL
eng_den_utm_cluster.to_sql('eng_den_utm_cluster', sqlEngine, if_exists='replace', index=True)
fr_den_utm_cluster.to_sql('fr_den_utm_cluster', sqlEngine, if_exists='replace', index=True)
local_den_utm_cluster.to_sql('local_den_utm_cluster', sqlEngine, if_exists='replace', index=True)

con.close()

