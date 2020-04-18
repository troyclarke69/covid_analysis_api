import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import sqlite3
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True

CORS(app)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '''<h1>This is the coronaAPI</h1>'''

# test: 127.0.0.1:5000/corona/addRow?intId=1&country=Canada&province=Ontario&cases=100&deaths=30&recovered=44
@app.route('/corona/addRow', methods=['GET', 'POST'])
def api_addRow():

    # if request.method == "POST":
        query_parameters = request.args

        # return "success"

        _intId = query_parameters.get('intId')
        _country = query_parameters.get('country')
        _province = query_parameters.get('province')
        _cases = query_parameters.get('cases')
        _deaths = query_parameters.get('deaths')
        _recovered = query_parameters.get('recovered')

        conn = sqlite3.connect('corona.db')
        conn.row_factory = dict_factory
        cur = conn.cursor()

        # ins_sql = 'INSERT INTO RawData(int_id, country, province, cases, deaths, recovered) VALUES (%s, %s, %s, %s, %s, %s)', (_intId, _country, _province, _cases, _deaths, _recovered))
        cur.execute('INSERT INTO RawData(int_id, country, province, cases, deaths, recovered) VALUES (?,?,?,?,?,?)', (_intId, _country, _province, _cases, _deaths, _recovered))
        # cur.commit()  #No commit on sqlite cursor
        conn.commit()
        conn.close()

        return _country


# test 127.0.0.1:5000/corona/add?jsonData="{["foo" : {"intId": 1, "country": "Canada", "province": "Ontario", "cases": 10, "deaths": 4, "recovered": 2}]}"
# test 127.0.0.1:5000/corona/add?jsonData="{"intId": "1", "country": "Canada", "province": "Ontario", "cases": "10", "deaths": "4", "recovered": "2"}"
@app.route('/corona/add', methods=['GET', 'POST'])
def api_add():

    # return '''<h1>This is the add routine'''

    query_parameters = request.args

    # return query_parameters

    # receiving the data via json as URL parameter
    jsonParam = query_parameters.get('jsonData')

    # return jsonParam

    # Parse the string passed in
    jsonData = json.loads(jsonParam)


    conn = sqlite3.connect('corona.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    # now parse the converted into individual fields
    _intId = jsonData["intId"]
    _country = jsonData["country"]
    _province = jsonData["province"]
    _cases = jsonData["cases"]
    _deaths = jsonData["deaths"]
    _recovered = jsonData["recovered"]

    ins_sql = 'INSERT INTO RawData(int_id, country, province, cases, deaths, recovered) VALUES(?,?,?,?,?,?);'
    cur.execute(ins_sql, _intId, _country, _province, _cases, _deaths, _recovered)
    cur.commit()


    return 1; #success

@app.route('/corona/raw/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('corona.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    raw = cur.execute('SELECT * FROM RawData;').fetchall()

    return jsonify(raw)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/corona/raw', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    int_id = query_parameters.get('int_id')
    country = query_parameters.get('country')

    query = "SELECT * FROM RawData WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if int_id:
        query += ' int_id=? AND'
        to_filter.append(int_id)
    if country:
        query += ' country=? AND'
        to_filter.append(int_id)
    if not (id or int_id or country):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('corona.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)

app.run()
