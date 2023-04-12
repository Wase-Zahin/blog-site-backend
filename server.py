from flask import Flask, jsonify, request, g
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DATABASE = 'cms.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        db = get_db()
        cursor = db.execute("SELECT id, title, username, description FROM blogs")
        res = [dict(row) for row in cursor.fetchall()]
        return jsonify(res)
    return jsonify([])

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    db = get_db()
    cursor = db.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    res = cursor.fetchone()
    if res is not None:
        return jsonify({'status':'login_yes', 'id':res[0]})
    return jsonify({'status': 'login_no'})

@app.route('/create', methods=['POST'])
def create():
    username = request.json.get('username')
    title = request.json.get('title')
    description = request.json.get('description')
    db = get_db()
    db.execute("INSERT INTO blogs (username, title, description) VALUES (?, ?, ?)", (username, title, description))
    db.commit()
    return jsonify({'status': 'success'})

@app.route('/description', methods=['POST'])
def detail():
    id = request.json.get('id')
    db = get_db()
    cursor = db.execute("SELECT title, username, description FROM blogs WHERE id = ?", (id,))
    res = cursor.fetchone()
    if res is not None:
        return jsonify(dict(res))
    return jsonify({'status': 'not_found'})

if __name__ == '__main__':
    app.run(debug=False, port=8000)
