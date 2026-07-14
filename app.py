import os
import psycopg2
import json
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"DB Error: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS config_departments (name VARCHAR(255) PRIMARY KEY);
                CREATE TABLE IF NOT EXISTS config_committees (name VARCHAR(255) PRIMARY KEY);
                CREATE TABLE IF NOT EXISTS config_comm_sections (sec_num INTEGER PRIMARY KEY, title VARCHAR(255), description TEXT);
            ''')
            # Seed defaults
            cur.execute('SELECT COUNT(*) FROM config_departments')
            if cur.fetchone()[0] == 0:
                for d in ['CSE', 'Civil', 'ECE', 'EEE', 'BHS']: 
                    cur.execute('INSERT INTO config_departments (name) VALUES (%s)', (d,))
            conn.commit()
    except Exception as e:
        print(f"DB Init Error: {e}")
    finally:
        conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Fail"}), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT name FROM config_departments ORDER BY name')
            depts = [r['name'] for r in cur.fetchall()]
            cur.execute('SELECT name FROM config_committees ORDER BY name')
            comms = [r['name'] for r in cur.fetchall()]
            cur.execute('SELECT * FROM config_comm_sections ORDER BY sec_num')
            c_secs = cur.fetchall()
            return jsonify({"departments": depts, "committees": comms, "comm_sections": c_secs}), 200
    finally: conn.close()

@app.route('/api/config/<entity_type>', methods=['POST'])
def add_config(entity_type):
    conn = get_db_connection()
    data = request.json
    try:
        with conn.cursor() as cur:
            if entity_type == 'departments':
                cur.execute('INSERT INTO config_departments (name) VALUES (%s)', (data['name'],))
            elif entity_type == 'committees':
                cur.execute('INSERT INTO config_committees (name) VALUES (%s)', (data['name'],))
            elif entity_type == 'comm_sections':
                cur.execute('SELECT COALESCE(MAX(sec_num), 100) + 1 FROM config_comm_sections')
                next_sec = cur.fetchone()[0]
                cur.execute('INSERT INTO config_comm_sections (sec_num, title, description) VALUES (%s, %s, %s)', 
                            (next_sec, data['title'], data.get('description', '')))
            conn.commit()
            return jsonify({"success": True}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally: conn.close()

@app.route('/api/config/<entity_type>/<path:item_id>', methods=['DELETE', 'PUT'])
def modify_config(entity_type, item_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if request.method == 'DELETE':
                if entity_type == 'departments': cur.execute('DELETE FROM config_departments WHERE name = %s', (item_id,))
                elif entity_type == 'committees': cur.execute('DELETE FROM config_committees WHERE name = %s', (item_id,))
                elif entity_type == 'comm_sections': cur.execute('DELETE FROM config_comm_sections WHERE sec_num = %s', (item_id,))
            elif request.method == 'PUT':
                data = request.json
                if entity_type == 'comm_sections':
                    cur.execute('UPDATE config_comm_sections SET title = %s, description = %s WHERE sec_num = %s', 
                                (data['title'], data.get('description', ''), item_id))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Fail"}), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT id, name, role, dept FROM users WHERE id = %s AND pass = %s', (data.get('id'), data.get('pass')))
            user = cur.fetchone()
            if user: return jsonify({"success": True, "user": user}), 200
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    finally: conn.close()

@app.route('/api/users', methods=['GET', 'POST'])
def manage_users():
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                cur.execute('SELECT id, name, role, dept FROM users')
                return jsonify(cur.fetchall()), 200
            if request.method == 'POST':
                data = request.json
                cur.execute('INSERT INTO users (id, name, role, dept, pass) VALUES (%s, %s, %s, %s, %s)',
                            (data.get('id'), data.get('name'), data.get('role'), data.get('dept'), data.get('pass')))
                conn.commit()
                return jsonify({"success": True}), 201
    finally: conn.close()

@app.route('/api/users/<user_id>', methods=['PUT', 'DELETE'])
def modify_user(user_id):
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Fail"}), 500
    try:
        with conn.cursor() as cur:
            if request.method == 'PUT':
                data = request.json
                cur.execute('UPDATE users SET id=%s, name=%s, role=%s, dept=%s WHERE id=%s',
                            (data.get('id', user_id), data.get('name'), data.get('role'), data.get('dept'), user_id))
                conn.commit()
                return jsonify({"success": True}), 200
            if request.method == 'DELETE':
                cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
                conn.commit()
                return jsonify({"success": True}), 200
    finally: conn.close()

@app.route('/api/submissions', methods=['GET', 'POST'])
def manage_submissions():
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                cur.execute('SELECT * FROM submissions ORDER BY created_at DESC')
                subs = cur.fetchall()
                for s in subs:
                    if s.get('created_at'): s['created_at'] = s['created_at'].isoformat()
                return jsonify(subs), 200
            if request.method == 'POST':
                data = request.json
                cur.execute('''INSERT INTO submissions (id, dept, month, year, status, sections, complete_pct, report_data) 
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                            (data.get('id'), data.get('dept'), data.get('month'), data.get('year'), 
                             data.get('status'), data.get('sections'), data.get('completePct'), json.dumps(data.get('reportData'))))
                conn.commit()
                return jsonify({"success": True}), 201
    finally: conn.close()

@app.route('/api/notifications', methods=['GET', 'POST'])
def manage_notifications():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Fail"}), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                cur.execute('SELECT * FROM notifications ORDER BY time DESC LIMIT 50')
                rows = cur.fetchall()
                return jsonify(rows), 200
            if request.method == 'POST':
                data = request.json
                cur.execute('INSERT INTO notifications (text, time, type, target) VALUES (%s, %s, %s, %s)',
                            (data.get('text'), data.get('time'), data.get('type'), data.get('target')))
                conn.commit()
                return jsonify({"success": True}), 201
    finally: conn.close()

if __name__ == '__main__':
    app.run(debug=True)
