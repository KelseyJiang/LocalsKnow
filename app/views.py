from flask import render_template, request
from app import app
import pymysql as mdb
from a_Model import ModelIt
from datatable import assign_datatable
import json
import globals




@app.route('/')
def homing():
    return render_template("input.html")


@app.route('/index')
def webindex():
    return render_template("input.html")

@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/input')
def cities_input():
  return render_template("input.html")

@app.route('/output')
def cities_output():
  db = mdb.connect(user= globals.webuser, host= globals.webhost, db="HelloParis", charset='utf8')
  #pull 'language' and 'city' from input field and store it
  language = request.args.get('language')
  #city = request.args.get('city')
  mydatatable = assign_datatable(lang = language)[0]
  rankby = assign_datatable(lang = language)[1]
  #mydatatable = assign_datatable(lang = language, city = city)[0]
  #rankby = assign_datatable(lang = language, city = city)[1]
  #col = ['#6E6E6E', '#FF0000','#610B0B', '#01DFD7','#DF7401','#DBA901','#D7DF01','#A5DF00','#74DF00','#3ADF00','#00BFFF','#0080FF','#0040FF','#0000FF','#4000FF','#FE2EF7', '#5F4C0B','#61380B','#2E2E2E']
 
  #col =  ['#6E6E6E','#FF0303','#F16701','#EA9A01','#E3CC00','#DDFF00','#B6FF00','#90FF00','#6AFF00','#44FF00','#33F33F','#22E87E','#11DDBD','#00D2FC','#069DED','#0D69DF','#1334D0','#1A00C2','#FF00FF']
 
  col = ['#6E6E6E','#FF0202','#FF4A02','#FFB002','#FFF302','#A7FF02','#40FF00','#167139','#00FFDE','#00B3FF','#1456FC','#6072E8','#1C1CFD','#761CFD','#B453E9','#F300FF','#55541C','#463011','#284100']
  with db:
    cur = db.cursor()
    cur.execute("SELECT loc_name, loc_id, loc_latitude, loc_longitude, cluster, photo FROM %s ORDER BY %s DESC;" % (mydatatable, rankby))
    query_results = cur.fetchall()
    
    
    sites = []
    site_color =[]
    for result in query_results:
        sites.append(dict(name=result[0], latitude=result[2], longitude = result[3], cluster = result[4], url = '<a><img src=%s height=\'300px\' width=\'250px\'/></a>' % result[5]))
    site_coords = [(site['latitude'], site['longitude']) for site in sites]
    site_cluster = [site['cluster']+1 for site in sites]
    site_name = [site['name'] for site in sites]
    site_url = [site['url'] for site in sites] #added
    
    for i in range(len(site_coords)):
        site_color.append(col[site_cluster[i]])
    
    if language == "english":
           greetings = "Here's where English speakers go!"
           colcode = "/static/english.png"
    elif language == "french": 
           greetings = "Here's where French speakers go!"
           colcode = "/static/french.png"
    else:
         greetings = "Here's where Parisian locals go!"
         colcode = "/static/locals.png"
        
    return render_template('output.html', 
                            cities=sites, 
                            name = json.dumps(list(site_name)),
                            coords = json.dumps(list(site_coords)),
                            color = json.dumps(list(site_color)),
                            colorcode = colcode,
                            url = json.dumps(list(site_url)), #added
                            greetings = greetings,
                            length = len(site_coords))
  
