''' This file is exported from IPython Notebook'''
from sqlalchemy import create_engine
from sqlalchemy.types import String 
import pandas as pd
from unidecode import unidecode

# Accessing data with the pymysql driver
# Database info
username='root'
password=''
server='localhost'
databaseName='HelloParis'

#Create connection with MySQL database
engineString = 'mysql+pymysql://'+ username +':'+ password +'@'+ server +'/'+databaseName + '?charset=utf8mb4'
#con = engine.connect()
sqlEngine = create_engine(engineString)
con = sqlEngine.connect()

# Query MySQL for location, users and language data
query = "Select * FROM paris_lang_loc WHERE prob > 0.95 AND loc_name NOT IN ('Paris','Paris, France','DROP')"
sqlResult = con.execute(query)
paris_lang_loc = pd.DataFrame(sqlResult.fetchall())
paris_lang_loc.columns = sqlResult.keys()

# Drop duplicated users in any given site
paris_lang_loc = paris_lang_loc.drop_duplicates(subset=['userid','loc_name'])

paris_lang_loc['loc_name'] = [unidecode(i).lower() for i in list(paris_lang_loc.loc_name)]

# Correct geo-location bugs in the database, making sure that each attraction is mapped at the exact location in the web app
paris_lang_loc.loc[paris_lang_loc.loc_name == 'eiffel tower','loc_latitude'] = 48.858603
paris_lang_loc.loc[paris_lang_loc.loc_name == 'eiffel tower','loc_longitude'] = 2.294465
paris_lang_loc.loc[paris_lang_loc.loc_name == 'eiffel tower','loc_id'] = 16334271
paris_lang_loc.loc[paris_lang_loc.loc_id == 165523447,'loc_latitude'] = 48.860791
paris_lang_loc.loc[paris_lang_loc.loc_id == 165523447,'loc_longitude'] = 2.337703
paris_lang_loc.loc[paris_lang_loc.loc_name == 'place de la republique',['loc_latitude','loc_longitude']] = [48.867735, 2.363802]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'ile saint-louis',['loc_latitude','loc_longitude']] = [48.851944,2.356667]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'cafe de flore',['loc_latitude','loc_longitude']] = [48.854149,2.332622]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'la villette',['loc_latitude','loc_longitude']] = [48.887920,2.378287]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'jardin des plantes',['loc_latitude','loc_longitude']] = [48.843694, 2.360047]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'a la maison',['loc_latitude','loc_longitude']] = [48.866643,2.309037]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'louvre',['loc_name','loc_latitude','loc_longitude']] = ['musee du louvre',48.860791,2.337703]            
paris_lang_loc.loc[paris_lang_loc.loc_id == 83214307,['loc_name','loc_latitude','loc_longitude']] = ['musee du louvre',48.860791,2.337703]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'le louvre',['loc_name','loc_latitude','loc_longitude']] = ['musee du louvre',48.860791,2.337703]            
paris_lang_loc.loc[paris_lang_loc.loc_id == 267548559,['loc_latitude','loc_longitude']] = [48.851617, 2.351607]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'gare du nord',['loc_latitude','loc_longitude']] = [48.880967, 2.355336]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'moulin rouge',['loc_latitude','loc_longitude']] = [48.884127, 2.332257]            

paris_lang_loc.loc[paris_lang_loc.loc_name == 'moulin rouge',['loc_latitude','loc_longitude']] = [48.884127, 2.332257]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'showcase',['loc_latitude','loc_longitude']] = [48.864288, 2.314006]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'le grand palais',['loc_name','loc_latitude','loc_longitude']] = ['grand palais', 48.866151, 2.312513]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'paradis du fruit - montparnasse',['loc_latitude','loc_longitude']] = [48.841179, 2.323596]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'arc de triomphe du carrousel',['loc_latitude','loc_longitude']] = [48.861737, 2.332882]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'mongmareuddeueondeog',['loc_name','loc_latitude','loc_longitude']] = ['sacre-coeur, paris',48.88600,2.341375]            
paris_lang_loc.loc[paris_lang_loc.loc_name == 'sacre-coeur, montmartre',['loc_name','loc_latitude','loc_longitude']] = ['musee du louvre',48.88600,2.341375]            
  

# Some location names in the database do not associate with any attractions; these location names are dropped from the database
paris_lang_loc = paris_lang_loc.drop(paris_lang_loc[paris_lang_loc.loc_name == 'white trash america'].index)
paris_lang_loc = paris_lang_loc.drop(paris_lang_loc[paris_lang_loc.loc_name == 'office'].index)
paris_lang_loc = paris_lang_loc.drop(paris_lang_loc[paris_lang_loc.loc_name == 'la poste'].index)
paris_lang_loc = paris_lang_loc.drop(paris_lang_loc[paris_lang_loc.loc_name == 'place de clichy'].index)
paris_lang_loc = paris_lang_loc.drop(paris_lang_loc[paris_lang_loc.loc_name == 'franprix'].index)
paris_lang_loc = paris_lang_loc.drop(paris_lang_loc[paris_lang_loc.loc_name == 'chez moi'].index)
paris_lang_loc = paris_lang_loc.drop(paris_lang_loc[paris_lang_loc.loc_name == 'anvers'].index)

# Save the dataframe to MySQL database
paris_lang_loc_corrected = paris_lang_loc.reset_index(drop= True)
paris_lang_loc_corrected.to_sql('paris_lang_loc_corrected2', sqlEngine, if_exists='replace', index=True)
con.close()