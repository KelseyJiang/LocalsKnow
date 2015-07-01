# Export from IPython Notebook
get_ipython().magic(u'matplotlib inline')
from instagram.client import InstagramAPI
import pandas as pd
import numpy as np
import json
import requests
import time, datetime
from langdetect import  detect_langs
import re 


# Load instagram API data; Paris, July 2014
insta_paris = pd.read_csv('insta_paris_July.csv',encoding='utf-8') 


# Extract captions; remove emojis; extract hashtags
        
def emoji_tag_remove(mytext):
    try:
        Cap_clean = mytext.encode('ascii', 'ignore')
        Cap_clean1 = re.sub(r'@\w*',' ', Cap_clean) 
        Cap_clean2 = re.sub(r'#',' ', Cap_clean1) 
        Cap_clean3 = re.sub(r'\n',' ', Cap_clean2) 
        Cap_clean4 = re.sub(r' +',' ', Cap_clean3) 
    except AttributeError:
        return None
    except TypeError:
        return None
    mytext = Cap_clean4
    return mytext
        
Cap_clean = [emoji_tag_remove(insta_paris['caption'][i]) for i in np.arange(0,len(insta_paris))]
insta_paris['caption'] = Cap_clean

# Delete short strings that can cause biases in language detection 
def rm_short_str(entry):
    try:
        if len(entry) < 20:
            return ''
        else:
            return entry
    except:
        return None

Cap_rm_short = [rm_short_str(i) for i in insta_paris['caption']]
insta_paris['caption'] = Cap_rm_short

# Drop data entries that does not come with media captions
insta_paris_cap = insta_paris[np.logical_and(pd.notnull(insta_paris['caption']) , insta_paris['caption']!= '')].reset_index(drop = True)
insta_paris_cap_res = insta_paris_cap[insta_paris_cap['caption']!= ' '].reset_index(drop = True)
insta_paris_cap_res.shape

# Language detection: determine the corresponding language using Naive Bayes classifier
# Output: the estimated language for each caption with the corresponding probability
def which_lan(cap_clean,rownum):
    try:
        lang_temp = Series(str(detect_langs(cap_clean[rownum])[0]).split(':')[0])
        lang_prob_temp = Series(str(detect_langs(cap_clean[rownum])[0]).split(':')[1])
    except:
        return None
    print rownum
    res = concat([lang_temp, lang_prob_temp], axis=1)
    return res 
    

def build_lan_table(DF,indexmin,indexmax):
    #dfs = [which_lan(df['caption'],r) for r in np.arange(indexmin,indexmax)]
    dfs = [concat([DF.loc[[r]].reset_index(drop=True),which_lan(DF['caption'],r)],axis = 1) for r in np.arange(indexmin,indexmax)]
    dfs = [d for d in dfs if d is not None]
    return pd.concat(dfs, ignore_index=True)

# Process a quarter of the database each time. Saves time during the debugging process.
lang_df_5000 = build_lan_table(insta_paris_cap_res,0,5000)
lang_df_10000 = build_lan_table(insta_paris_cap,5000,10000)
lang_df_15000 = build_lan_table(insta_paris_cap,10000,15000)
lang_df_25010 = build_lan_table(insta_paris_cap,15000,25010)

insta_paris_lan = DataFrame()
insta_paris_lan = insta_paris_lan.append(pandas.DataFrame(data=lang_df_5000),ignore_index=True)
insta_paris_lan = insta_paris_lan.append(pandas.DataFrame(data=lang_df_10000),ignore_index=True)
insta_paris_lan = insta_paris_lan.append(pandas.DataFrame(data=lang_df_15000),ignore_index=True)
insta_paris_lan = insta_paris_lan.append(pandas.DataFrame(data=lang_df_25010),ignore_index=True)

insta_paris_lan.to_csv('insta_paris_July_lan.csv',encoding='utf-8',index=False)




