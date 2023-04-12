from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from threading import Lock

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

lock = Lock()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("cms.db", check_same_thread=False)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        with lock:
            cur = get_db().cursor()
            sql = "SELECT id, title, username, description FROM blogs"
            cur.execute(sql)
            res = cur.fetchall()
            if res:
                return jsonify(res)
    return jsonify()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with lock:
            cur = get_db().cursor()
            username = request.json.get('username')
            password = request.json.get('password')
            sql = "SELECT * FROM users WHERE username = ? AND password = ?"
            user = (username, password)
            cur.execute(sql, user)
            res = cur.fetchone()
            if res:
                userid = res['id']
                return jsonify({'status':'login_yes', 'id':userid})
    return jsonify({'status': 'login_no'})

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        with lock:
            cur = get_db().cursor()
            username = request.json.get('username')
            title = request.json.get('title')
            description = request.json.get('description')
            sql = "INSERT INTO blogs(username, title, description) VALUES (?, ?, ?);"
            values = (username, title, description)
            cur.execute(sql, values)
            get_db().commit()
            return ("Submitted successfully!")
    return "Sorry, submission failed."

@app.route('/description', methods=['GET', 'POST'])
def detail():
    if request.method == 'POST':
        with lock:
            cur = get_db().cursor()
            id = request.json.get('id')
            sql = "SELECT title, username, description FROM blogs WHERE id = ?"
            cur.execute(sql, (id,))
            res = cur.fetchone()
            if res:
                return jsonify(res)
    return "Sorry the content is not available"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
