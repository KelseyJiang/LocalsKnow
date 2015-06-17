from flask import render_template, request
from app import app
import pymysql as mdb
from a_Model import ModelIt
from datatable import assign_datatable
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
  #pull 'ID' from input field and store it
  language = request.args.get('language')
  city = request.args.get('city')
  mydatatable = assign_datatable(lang = language, city = city)
  
  with db:
    cur = db.cursor()
    #just select the city from the world_innodb that the user inputs
    cur.execute("SELECT loc_name, loc_id, loc_latitude, loc_longitude, fr_count, eng_count, total_count FROM %s ORDER BY eng_count DESC;" % mydatatable)
    #cur.execute("SELECT Name, CountryCode,  Population FROM City WHERE Name='%s';" % city)
    query_results = cur.fetchall()
    
    
    sites = []
    for result in query_results:
        sites.append(dict(name=result[0], latitude=result[2], longitude = result[3]))
    return render_template('output.html', cities=sites)
  
 #  #call a function from a_Model package. note we are only pulling one result in the query
#   pop_input = cities[0]['latitude']
#   the_result = ""
#   #the_result = ModelIt(city, pop_input)
#   return render_template("output.html", cities = sites, the_result = the_result)