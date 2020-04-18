import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import sqlite3

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
    return '''<h1>This is the pyX API</h1>
<p></p>'''

@app.route('/api/daily', methods=['GET'])
def api_daily():

# Note: The 'data.sqlite' database is created through converting SQL database: Googster_dump to sqlite
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
