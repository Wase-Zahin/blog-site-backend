from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from threading import Lock

conn = sqlite3.connect("cms.db", check_same_thread=False)

def dict_factory(cursor,row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn.row_factory = dict_factory
cursor = conn.cursor()
lock = Lock()

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        sql = "select id, title, username, description from blogs"
        cursor.execute(sql)
        res = cursor.fetchall()
        if res:
            return jsonify(res)
    return jsonify()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        sql = "select * from users where username = ? and password = ?"
        user = (username, password)
        cursor.execute(sql, user)
        res = cursor.fetchone()
        if res:
            userid = res['id']
            return jsonify({'status':'login_yes', 'id':userid})
    return jsonify({'status': 'login_no'})

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        username = request.json.get('username')
        title = request.json.get('title')
        description = request.json.get('description')
        sql = "insert into blogs(username, title, description) values (?, ?, ?);"
        values = (username, title, description)
        cursor.execute(sql, values)
        conn.commit()
        return ("Submitted successfully!")
    return "Sorry, submission failed."

@app.route('/description', methods=['GET', 'POST'])
def detail():
    if request.method == 'POST':
        id = request.json.get('id')
        sql = "select title, username, description from blogs where id = ?"
        cursor.execute(sql, id)
        res = cursor.fetchone()
        print(res)
        if res:
            return res
    return "Sorry the content is not available"

app.run(debug=True, port=8000)
