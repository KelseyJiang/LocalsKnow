# This file is exported from IPython Notebook
from sqlalchemy import create_engine
from sqlalchemy.types import String 
from pandas import *
from unidecode import unidecode

# Accessing data with the pymysql driver
# Database info
username='root'
password=''
server='localhost'
databaseName='HelloParis'

#Create connection with sql database
engineString = 'mysql+pymysql://'+ username +':'+ password +'@'+ server +'/'+databaseName + '?charset=utf8mb4'
sqlEngine = create_engine(engineString)
con = sqlEngine.connect()

# Data query. paris_lang_loc_corrected contains user, site, geo-location data in Paris during July 2014 
query = "Select * FROM paris_lang_loc_corrected2 WHERE prob > 0.95 AND loc_name NOT IN ('Paris','Paris, France','DROP')"
sqlResult = con.execute(query)
paris_lang_loc_corrected = pd.DataFrame(sqlResult.fetchall())
paris_lang_loc_corrected.columns = sqlResult.keys()

# drop duplicated users for each attraction
paris_lang_loc_corrected = paris_lang_loc_corrected.drop_duplicates(subset=['userid','loc_name'])

# Label locals
# Data query. all_user_history contains users travel history in Jan, Feb, Mar 2014
# In all_user_history, local parisians are labled as "locals", other french speakers labeled as "regional"
query = "Select * FROM all_user_history"
sqlResult = con.execute(query)
all_user_history = pd.DataFrame(sqlResult.fetchall())
all_user_history.columns = sqlResult.keys()

all_user_history['userid'] = [int(id) for id in all_user_history.userid]

# Merge July database with users' travel history
paris_lang_loc_local = merge(paris_lang_loc_corrected, all_user_history[['userid','group']], how='left', on=['userid'])

# Lable English speakers as visitor 
paris_lang_loc_local['group'] = paris_lang_loc_local['group'].fillna('visitor')
paris_lang_loc_local.rename(columns={'group':'user_group'}, inplace=True)

# Save dataframe to MySQL Database
paris_lang_loc_local.to_sql('paris_lang_loc_local', sqlEngine, if_exists='replace', index=True)

con.close()