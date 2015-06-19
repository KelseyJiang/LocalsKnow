from flask import render_template, request
from app import app
import pymysql as mdb
from a_Model import ModelIt
from datatable import assign_datatable
import json
import globals


db = mdb.connect(user= globals.webuser, host= globals.webhost, db="HelloParis", charset='utf8')

# @app.route('/')
# @app.route('/index')
# def index():
#     return render_template("index.html",
#        title = 'Home', user = { 'nickname': 'Miguel' },
#        )
# 
# @app.route('/db')
# def cities_page():
#     with db:
#         cur = db.cursor()
#         cur.execute("SELECT Name FROM City LIMIT 15;")
#         query_results = cur.fetchall()
#     cities = ""
#     for result in query_results:
#         cities += result[0]
#         cities += "<br>"
#     return cities

@app.route("/db_test")
def sites_fancy():
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM eng_den_utm_cluster ORDER BY eng_count DESC;")
        query_results = cur.fetchall()
    sites = []
    for result in query_results:
        sites.append(dict(name=result[1], latitude=result[3], longitude = result[4]))
    return render_template('cities.html', cities=cities)
    
@app.route('/input')
def cities_input():
  return render_template("input.html")

@app.route('/output')
def cities_output():
  #pull 'language' and 'city' from input field and store it
  language = request.args.get('language')
  city = request.args.get('city')
  mydatatable = assign_datatable(lang = language, city = city)[0]
  rankby = assign_datatable(lang = language, city = city)[1]
  col = ['#6E6E6E', '#610B0B','#FF0000', '#DF3A0', '#DF7401','#DBA901', '#D7DF01', '#A5DF00', '#74DF00','#3ADF00','#00BFFF','#0080FF','#0040FF','#0000FF','#4000FF','#FE2EF7', '#5F4C0B','#61380B','#2E2E2E']
  #col = ['#2E2E2E','#DF0101','#8A0808','#FF8000','#BFFF00','#40FF00','#00FFFF','#0040FF','#8000FF','#F781F3','#F5A9BC','#FF8000','#B18904','#B18904','#B18904','#B18904','#B18904','#B18904','#B18904','#B18904']
 
 
  with db:
    cur = db.cursor()
    #just select the city from the world_innodb that the user inputs
    cur.execute("SELECT loc_name, loc_id, loc_latitude, loc_longitude, cluster FROM %s ORDER BY %s DESC;" % (mydatatable, rankby))
    query_results = cur.fetchall()
    
    
    sites = []
    site_color =[]
    for result in query_results:
        sites.append(dict(name=result[0], latitude=result[2], longitude = result[3], cluster = result[4])) 
    site_coords = [(site['latitude'], site['longitude']) for site in sites]
    site_cluster = [site['cluster']+1 for site in sites]
    
    for i in range(len(site_coords)):
        site_color.append(col[site_cluster[i]])
        print col[site_cluster[i]]
        
    return render_template('output.html', 
                            cities=sites, 
                            coords = json.dumps(list(site_coords)),
                            color = json.dumps(list(site_color)),
                            length = len(site_coords))
  
 #  #call a function from a_Model package. note we are only pulling one result in the query
#   pop_input = cities[0]['latitude']
#   the_result = ""
#   #the_result = ModelIt(city, pop_input)
#   return render_template("output.html", cities = sites, the_result = the_result)