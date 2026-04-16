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

@app.route('/')
def home():
    return render_template('index.html')

def get_db_connection():
    try:
        conn = psycopg2.connect(
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT'),
            database=os.environ.get('DB_NAME')
        )
        return conn
    except Exception as e:
        print(f"DB Error: {e}")
        return None

# --- AUTH & USERS ---
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

@app.route('/api/users/<user_id>/password', methods=['PUT'])
def change_password(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('UPDATE users SET pass = %s WHERE id = %s', (request.json.get('newPass'), user_id))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

@app.route('/api/users', methods=['GET', 'POST'])
def manage_users():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                cur.execute('SELECT id, name, role, dept FROM users ORDER BY role, name')
                return jsonify(cur.fetchall()), 200
            if request.method == 'POST':
                data = request.json
                cur.execute('INSERT INTO users (id, pass, name, role, dept) VALUES (%s, %s, %s, %s, %s)',
                            (data.get('id'), data.get('pass', 'Pass@123'), data.get('name'), data.get('role'), data.get('dept', '')))
                conn.commit()
                return jsonify({"success": True}), 201
    finally: conn.close()

@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('UPDATE users SET name = %s, role = %s, dept = %s WHERE id = %s',
                        (request.json.get('name'), request.json.get('role'), request.json.get('dept', ''), user_id))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

@app.route('/api/users/<user_id>', methods=['DELETE'])
def  delete_user(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

# --- SUBMISSIONS ---
@app.route('/api/submissions', methods=['GET', 'POST'])
def manage_submissions():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                role = request.args.get('role')
                dept = request.args.get('dept')
                if role in ['Super Admin', 'Principal', 'Admin']:
                    cur.execute('SELECT * FROM submissions ORDER BY created_at DESC')
                else:
                    dept_list = [d.strip() for d in dept.split(',')] if dept else []
                    cur.execute('SELECT * FROM submissions WHERE dept = ANY(%s) ORDER BY created_at DESC', (dept_list,))
                rows = cur.fetchall()
                for row in rows:
                    if row.get('created_at'): row['created_at'] = row['created_at'].isoformat()
                return jsonify(rows), 200

            if request.method == 'POST':
                data = request.json
                cur.execute('''INSERT INTO submissions (id, dept, month, year, status, sections, complete_pct, report_data) 
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *''',
                            (data.get('id'), data.get('dept'), data.get('month'), data.get('year'), 
                             data.get('status'), data.get('sections'), data.get('completePct'), json.dumps(data.get('reportData'))))
                new_sub = cur.fetchone()
                if new_sub.get('created_at'): new_sub['created_at'] = new_sub['created_at'].isoformat()
                conn.commit()
                return jsonify({"success": True, "submission": new_sub}), 201
    finally: conn.close()

# --- CALENDAR ---
@app.route('/api/calendar', methods=['GET', 'POST'])
def manage_calendar():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                cur.execute('SELECT id, TO_CHAR(event_date, \'Mon DD\') as date, event_title as event, event_type as type FROM calendar_events ORDER BY event_date ASC')
                return jsonify(cur.fetchall()), 200
            if request.method == 'POST':
                data = request.json
                cur.execute('INSERT INTO calendar_events (event_date, event_title, event_type) VALUES (%s, %s, %s)',
                            (data.get('date'), data.get('event'), data.get('type')))
                conn.commit()
                return jsonify({"success": True}), 201
    finally: conn.close()

# --- SECTIONS ---
@app.route('/api/sections', methods=['GET', 'POST'])
def manage_sections():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                cur.execute('SELECT * FROM form_sections ORDER BY sec_num ASC')
                return jsonify(cur.fetchall()), 200
            if request.method == 'POST':
                data = request.json
                cur.execute('SELECT COALESCE(MAX(sec_num), 22) + 1 FROM form_sections')
                next_sec = cur.fetchone()['?column?']
                cur.execute('INSERT INTO form_sections (sec_num, title, description) VALUES (%s, %s, %s)',
                            (next_sec, data.get('title'), data.get('description', '')))
                conn.commit()
                return jsonify({"success": True}), 201
    finally: conn.close()

@app.route('/api/users/<user_id>', methods=['DELETE'])
def remove_user(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(debug=True, port=port)