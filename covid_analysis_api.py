import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import sqlite3
import requests
import json
import pyodbc
import urllib.request

app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

#This will run run.py at 11PM daily. Note that we kick off the run 
# at 11PM and fetch the results at 12AM. This gives ParseHub plenty of margin to finish the job.
# crontab -e
# 0 23 * * * python /tmp/parsehub/run.py

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/api/download', methods=['GET'])
def api_download():
# Note: This python API uses a sqlite database named: data.sqlite

    api_url_base = 'https://pomber.github.io/covid19/timeseries.json'
    # may not need headers?
    headers = {'Content-Type': 'application/json'}

    # using requests module:
    response = requests.get(api_url_base, headers=headers)

    # using urllib:
    r = urllib.request.urlopen(api_url_base)

    result = ''

    if response.status_code == 200:

        # decode json to object (dict):

        # result = json.loads(response.content.decode('utf-8'))

        # urllib:
        data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        
        # print(result)
        # print(type(result)) # 'dict'

        # encode object to json (str) ** this response already returns json (this playing around)
        # dump = json.dumps(response.content.decode('utf-8'))
        # # print(dump)
        # print(type(dump))

        conn = sqlite3.connect('data.sqlite')
        conn.row_factory = dict_factory
        cur = conn.cursor()
        
        for json_inner_array in data:
            print(json_inner_array)
            for json_data in json_inner_array:
                print(json_data[0])

        # for record in result:
        #     country = record
            # print(country)
            # date1 = record["confirmed"]          
            # print(date1)
            # for r in record:
            #     confirmed = r['confirmed']
                # print(confirmed)

            # print(json.dumps(response.content.decode('utf-8')))
            # cur.execute('INSERT INTO dbo.Moth (cols) VALUES( vals )')
            # conn.commit()

        cur.close()
        conn.close()

        return 'success'

        # country = result
        # return country

    else:
        return None
        
    # return jsonify(all_rows)


@app.route('/', methods=['GET'])
def home():
    return '''
        <span><h1>COVID-ANALYSIS-API</h1></span>
        <p>Project: <h4>./repos/python-flask-API</h4></p>
        <p>Python File: <h4>./corona-analysis.py</h4></p>
        <p>Seed Data/Source API: <em>https://pomber.github.io/covid19/timeseries.json</em></p>
        <p><h2>Development Notes (Last Update: 4/15/2020):</h2></p>
        <p><b>Notes on Route: 127.0.0.1:5000/api/daily</b></p>
        <ul>
            <li>This python API uses a sqlite database named: <em>data.sqlite</em></li>
            <li>The <em>data.sqlite</em> database is created through converting SQL database: <em>Googster_dump</em> to sqlite</li>
            <li><em>Googster_dump</em> resides in the 'DESKTOP-<>' MSSQL connection </li>
            <li>The conversion of SQL => SQLITE is done through <em>rebasedata.com</em> </li>
            <li>The originating data is retrieved through the <em>Googster</em> (Path: ./Bug) .NET/MVC project.</li>
            <li>After running the download of data through .NET, running the custom SQL scripts developed
            (found in <em>./Googster/SQL</em> folder) will parse the data into the <em>Googster.Moth</em> table. <br>
            Scripts: 'CORONA Dailies Parsing WITH' & 'CORONA Dailies Parsing TROUGH' </li>
            <li>This table is then IMPORTED into the <em>Googster_dump</em> database (through Tasks-Import in SQL)</li>
        </ul>
        <h2>Endpoints:</h2>
        <p>/api/daily</p>
        <p>/api/daily/country **hardcoded to country: 'Canada', province: 'Ontario', category: 1 (cases)</p>
        <p><i>&nbsp;&nbsp;>> uses sample 'books.db':</i></p>
        <p>/api/v1/resources/books/all</p>
        <p>/api/v1/resources/books?published=2014</p>
        </p>
        '''

@app.route('/api/daily', methods=['GET'])
def api_daily():
# Note: This python API uses a sqlite database named: data.sqlite
# The 'data.sqlite' database is created through converting SQL database: Googster_dump to sqlite
# *** Googster_dump resides in the 'DESKTOP-x?x?x' SQL connected ***
# The conversion of SQL => SQLITE is done through rebasedata.com. 
# The originating data is retrieved through the 'Googster' (/Bug) .NET/MVC project.
# After running the download of data through .NET, running the custom SQL scripts developed 
# (found in /Googster/SQL folder) will parse the data into the Googster.Moth table. 
# This table is then IMPORTED into the Googster_dump database (through Tasks-Import in SQL)

    conn = sqlite3.connect('data.sqlite')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_rows = cur.execute('''SELECT Country, Province, CASE WHEN Category = '1' THEN 'Cases' 
        WHEN Category = '2' THEN 'Deaths' ELSE 'Recovered' END Category, Date1, Actual FROM "dbo.Moth"''').fetchall()

    return jsonify(all_rows)

@app.route('/api/daily/country', methods=['GET'])
def api_daily_country():
    # obtain params:
    # country, province + category?

    conn = sqlite3.connect('data.sqlite')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_rows = cur.execute('''SELECT Date1, Actual FROM "dbo.Moth"
        WHERE Category = "1" and Country = "Canada" and Province = "ontario" order by Date1''').fetchall()

    return jsonify(all_rows)

@app.route('/api/v1/resources/books/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_books = cur.execute('SELECT * FROM books;').fetchall()

    return jsonify(all_books)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/api/v1/resources/books', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    published = query_parameters.get('published')
    author = query_parameters.get('author')

    query = "SELECT * FROM books WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if published:
        query += ' published=? AND'
        to_filter.append(published)
    if author:
        query += ' author=? AND'
        to_filter.append(author)
    if not (id or published or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)

app.run()
