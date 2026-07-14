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
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"DB Error: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if not conn:
        print("Could not connect to database for initialization.")
        return
    try:
        with conn.cursor() as cur:
            # Create departments table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS departments (
                    code VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                )
            ''')
            # Create committees table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS committees (
                    name VARCHAR(255) PRIMARY KEY
                )
            ''')
            # Check if empty, insert defaults
            cur.execute('SELECT COUNT(*) FROM departments')
            if cur.fetchone()[0] == 0:
                depts = [
                    ('CSE', 'Computer Science Engineering'),
                    ('Civil', 'Civil Engineering'),
                    ('ECE', 'Electronics & Communication Engineering'),
                    ('EEE', 'Electrical & Electronics Engineering'),
                    ('BHS', 'Basic & Humanities Sciences')
                ]
                cur.executemany('INSERT INTO departments (code, name) VALUES (%s, %s)', depts)
            
            cur.execute('SELECT COUNT(*) FROM committees')
            if cur.fetchone()[0] == 0:
                comms = [
                    ('Anti Ragging and Discipline Committee',),
                    ('Internal Complaint Committee (ICC)',),
                    ('Student Grievances and Redressal Committee',),
                    ('SC/ST Committee',),
                    ('OBC Committee',),
                    ('Minorities Committee',),
                    ('R&D',),
                    ('Entrepreneurship, Startup and Innovation',),
                    ('Literary and Cultural Committee',),
                    ('Sports',),
                    ('SDC / Internship / Placement / III Cell / Career Guidance',),
                    ('Alumni / NSS',),
                    ('Maintenance Committee',),
                    ('Sustainable Development Goals (SDG)',),
                    ('Information Technology & Website',),
                    ('Canteen and Food Committee',),
                    ('Professional Bodies',),
                    ('Equity Committee',),
                    ('IQAC',)
                ]
                cur.executemany('INSERT INTO committees (name) VALUES (%s)', comms)
            conn.commit()
            print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing DB tables: {e}")
    finally:
        conn.close()

# Run initialization on startup
init_db()

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
                # Added 'id=%s' to the SET clause and 'data.get('id', user_id)' to the parameters
                cur.execute('UPDATE users SET id=%s, name=%s, role=%s, dept=%s WHERE id=%s',
                            (data.get('id', user_id), data.get('name'), data.get('role'), data.get('dept'), user_id))
                conn.commit()
                return jsonify({"success": True}), 200
            if request.method == 'DELETE':
                cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
                conn.commit()
                return jsonify({"success": True}), 200
    finally: conn.close()

@app.route('/api/users/<user_id>/password', methods=['PUT'])
def update_password(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            data = request.json
            cur.execute('UPDATE users SET pass=%s WHERE id=%s', (data.get('newPass'), user_id))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

# --- NOTIFICATIONS ---
@app.route('/api/notifications', methods=['GET', 'POST'])
def manage_notifications():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Fail"}), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                cur.execute('SELECT * FROM notifications ORDER BY time DESC LIMIT 50')
                rows = cur.fetchall()
                for row in rows:
                    if row.get('time'): row['time'] = row['time'].isoformat()
                    row['read'] = False 
                return jsonify(rows), 200

            if request.method == 'POST':
                data = request.json
                cur.execute('''INSERT INTO notifications (text, time, type, target) 
                               VALUES (%s, %s, %s, %s) RETURNING *''',
                            (data.get('text'), data.get('time'), data.get('type'), data.get('target')))
                new_notif = cur.fetchone()
                if new_notif.get('time'): new_notif['time'] = new_notif['time'].isoformat()
                conn.commit()
                return jsonify({"success": True, "notification": new_notif}), 201
    finally: conn.close()

@app.route('/api/notifications/<notif_id>', methods=['DELETE'])
def delete_notification(notif_id):
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Fail"}), 500
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM notifications WHERE id = %s', (notif_id,))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

# --- SUBMISSIONS ---
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

# --- CALENDAR ---
@app.route('/api/calendar', methods=['GET', 'POST'])
def manage_calendar():
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                cur.execute('SELECT * FROM calendar_events ORDER BY id ASC')
                return jsonify(cur.fetchall()), 200
            if request.method == 'POST':
                data = request.json
                cur.execute('INSERT INTO calendar_events (date, event, type) VALUES (%s, %s, %s)',
                            (data.get('date'), data.get('event'), data.get('type')))
                conn.commit()
                return jsonify({"success": True}), 201
    finally: conn.close()

@app.route('/api/calendar/<event_id>', methods=['DELETE'])
def remove_calendar_event(event_id):
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Fail"}), 500
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM calendar_events WHERE id = %s', (event_id,))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

@app.route('/api/calendar-docs', methods=['GET', 'POST'])
def manage_calendar_docs():
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                cur.execute('SELECT * FROM calendar_docs ORDER BY id DESC')
                return jsonify(cur.fetchall()), 200
            if request.method == 'POST':
                data = request.json
                cur.execute('INSERT INTO calendar_docs (title, "imageData", "isPDF", date) VALUES (%s, %s, %s, %s)',
                            (data.get('title'), data.get('imageData'), data.get('isPDF'), data.get('date')))
                conn.commit()
                return jsonify({"success": True}), 201
    finally: conn.close()

@app.route('/api/calendar-docs/<doc_id>', methods=['DELETE'])
def remove_calendar_doc(doc_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM calendar_docs WHERE id = %s', (doc_id,))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

# --- SECTIONS ---
@app.route('/api/sections', methods=['GET', 'POST'])
def manage_sections():
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                cur.execute('SELECT * FROM form_sections ORDER BY sec_num ASC')
                return jsonify(cur.fetchall()), 200
            if request.method == 'POST':
                data = request.json
                sec_num = data.get('sec_num')
                if not sec_num:
                    cur.execute('SELECT COALESCE(MAX(sec_num), 22) + 1 FROM form_sections')
                    sec_num = cur.fetchone()['?column?']
                cur.execute('INSERT INTO form_sections (sec_num, title, description) VALUES (%s, %s, %s)',
                            (sec_num, data.get('title'), data.get('description', '')))
                conn.commit()
                return jsonify({"success": True}), 201
    finally: conn.close()

@app.route('/api/sections/<sec_id>', methods=['PUT'])
def update_section(sec_id):
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Fail"}), 500
    try:
        with conn.cursor() as cur:
            data = request.json
            cur.execute('''
                INSERT INTO form_sections (sec_num, title, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (sec_num) DO UPDATE SET
                title = EXCLUDED.title, description = EXCLUDED.description
            ''', (int(sec_id), data.get('title'), data.get('description', '')))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

@app.route('/api/sections/<sec_id>', methods=['DELETE'])
def remove_section(sec_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM form_sections WHERE sec_num = %s', (sec_id,))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

# --- DEPARTMENTS ---
@app.route('/api/departments', methods=['GET', 'POST'])
def manage_departments():
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                cur.execute('SELECT * FROM departments ORDER BY code ASC')
                return jsonify(cur.fetchall()), 200
            if request.method == 'POST':
                data = request.json
                code = data.get('code')
                name = data.get('name')
                if not code or not name:
                    return jsonify({"error": "Missing code or name"}), 400
                cur.execute('INSERT INTO departments (code, name) VALUES (%s, %s) ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name', (code, name))
                # Also insert into departments_data if not exists
                cur.execute('INSERT INTO departments_data (dept) VALUES (%s) ON CONFLICT (dept) DO NOTHING', (code,))
                conn.commit()
                return jsonify({"success": True}), 201
    finally: conn.close()

@app.route('/api/departments/<code>', methods=['DELETE'])
def remove_department(code):
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Fail"}), 500
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM departments WHERE code = %s', (code,))
            cur.execute('DELETE FROM departments_data WHERE dept = %s', (code,))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

# --- COMMITTEES ---
@app.route('/api/committees', methods=['GET', 'POST'])
def manage_committees():
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if request.method == 'GET':
                cur.execute('SELECT * FROM committees ORDER BY name ASC')
                return jsonify(cur.fetchall()), 200
            if request.method == 'POST':
                data = request.json
                name = data.get('name')
                if not name:
                    return jsonify({"error": "Missing name"}), 400
                cur.execute('INSERT INTO committees (name) VALUES (%s) ON CONFLICT (name) DO NOTHING', (name,))
                conn.commit()
                return jsonify({"success": True}), 201
    finally: conn.close()

@app.route('/api/committees/<name>', methods=['DELETE'])
def remove_committee(name):
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Fail"}), 500
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM committees WHERE name = %s', (name,))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

# --- DEPARTMENTS DATA ---
@app.route('/api/departments-data', methods=['GET'])
def get_dept_data():
    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM departments_data')
            return jsonify(cur.fetchall()), 200
    finally: conn.close()

@app.route('/api/departments-data/<dept_id>', methods=['PUT'])
def update_dept_data(dept_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            data = request.json
            cur.execute('''
                INSERT INTO departments_data (dept, faculty, y1, y2, y3, y4, cse, ece, eee, civil, placed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (dept) DO UPDATE SET
                faculty = EXCLUDED.faculty, y1 = EXCLUDED.y1, y2 = EXCLUDED.y2, y3 = EXCLUDED.y3, y4 = EXCLUDED.y4,
                cse = EXCLUDED.cse, ece = EXCLUDED.ece, eee = EXCLUDED.eee, civil = EXCLUDED.civil, placed = EXCLUDED.placed
            ''', (dept_id, data.get('faculty', 0), data.get('y1', 0), data.get('y2', 0), data.get('y3', 0), data.get('y4', 0),
                  data.get('cse', 0), data.get('ece', 0), data.get('eee', 0), data.get('civil', 0), data.get('placed', 0)))
            conn.commit()
            return jsonify({"success": True}), 200
    finally: conn.close()

if __name__ == '__main__':
    app.run(debug=True)
