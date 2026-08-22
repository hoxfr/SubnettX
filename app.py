import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
from datetime import datetime
import threading
import hmac
import hashlib
import sqlite3
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# =========================================
# SUBNETTX — PRODUCTION FLASK SERVER
# =========================================
app = Flask(__name__)
app.secret_key = os.urandom(32)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attendance.db')
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'certificates')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
TOKEN_ROTATION_SECONDS = 3
SECRET_ROOM_SALT = b'SUBNETTX_CRYPTO_SALT_2026_ANTICHEAT'

import socket
def get_local_gateway_segment():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        parts = ip.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}."
    except Exception:
        return "127.0.0."

ACTIVE_GATEWAY_SEGMENT = get_local_gateway_segment()
print(f"[NETWORK] Active Gateway Bound to: {ACTIVE_GATEWAY_SEGMENT}*")
# ========================================================================
# DUAL-VECTOR PROXIMITY ENGINE STATE
# ========================================================================
import random
LEVC_STATE = {"active": False, "color": None, "issued_at": 0, "block_id": 0}
LEVC_TTL_MS = 3000  # 1.2s window — physical student reacts in ~600ms, stream cheater >1.5s
LEVC_COLORS = ["CRIMSON", "COBALT", "EMERALD"]

def get_ultrasonic_freq(time_block_id):
    """Deterministically derive an ultrasonic frequency (18000-20000 Hz) from the time block.
    VoIP codecs (Opus/Discord) aggressively low-pass filter above ~15kHz, destroying this signal."""
    seed = hmac.new(SECRET_ROOM_SALT, f"FREQ:{time_block_id}".encode(), hashlib.sha256).hexdigest()
    freq_offset = int(seed[:4], 16) % 2000  # 0-1999
    return 18000 + freq_offset




# ========================================================================
# LIVE SMTP EMAIL SERVER INTERFACE CONFIGURATION
# ========================================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "subnettx@gmail.com"
SMTP_PASSWORD = "sfwg hquf vxtm xqnk"
SENDER_EMAIL = "subnettx@gmail.com"


def send_async_email_worker(recipient_email, subject, body_text):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_text, 'plain'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        print(f"[MAIL SYSTEM] Live email dispatched to: {recipient_email}")
        return True
    except Exception as e:
        print(f"[MAIL SYSTEM ERROR] Delivery exception to {recipient_email}: {str(e)}")
        return False


# =========================================
# OPTIMIZED DATABASE CONNECTION LAYER
# Context-managed with WAL + NORMAL sync
# =========================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")

        # --- Table 1: Student Registry ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_registry (
                enrollment_id TEXT PRIMARY KEY,
                student_name TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT DEFAULT '',
                conducted_lectures INTEGER DEFAULT 0,
                attended_lectures INTEGER DEFAULT 0,
                percentage REAL DEFAULT 0.0
            )
        ''')

        # --- Table 2: Verification Logs ---
        cursor.execute("DROP TABLE IF EXISTS network_profiles")
        cursor.execute('''
            CREATE TABLE network_profiles (
                network_id TEXT PRIMARY KEY,
                segment_prefix TEXT,
                maximum_allowed_latency_ms INTEGER DEFAULT 150,
                network_type TEXT
            )
        ''')
        cursor.execute("INSERT OR IGNORE INTO network_profiles VALUES ('L_HALL_AP', '10.7.', 50, 'CLASSROOM')")

        cursor.execute("DROP TABLE IF EXISTS attendance_ledger")
        cursor.execute('''
            CREATE TABLE attendance_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enrollment_id TEXT NOT NULL,
                subject_code TEXT,
                date_stamped DATE,
                scan_timestamp DATETIME,
                source_ip TEXT,
                network_type TEXT,
                recorded_latency REAL,
                tracking_status TEXT
            )
        ''')

        cursor.execute("DROP TABLE IF EXISTS verification_logs")
        cursor.execute('''
            CREATE TABLE verification_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enrollment_id TEXT NOT NULL,
                token_submitted TEXT NOT NULL,
                expected_token TEXT,
                time_block_id INTEGER,
                client_timestamp REAL,
                server_timestamp REAL,
                status TEXT DEFAULT 'PENDING',
                detail TEXT DEFAULT '',
                source_ip TEXT,
                network_type TEXT,
                recorded_latency REAL,
                FOREIGN KEY (enrollment_id) REFERENCES student_registry(enrollment_id)
            )
        ''')

        # --- Table 3: Leave Tickets ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leave_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enrollment_id TEXT NOT NULL,
                ticket_type TEXT DEFAULT 'MEDICAL',
                reason TEXT,
                status TEXT DEFAULT 'PENDING',
                submitted_at REAL,
                reviewed_at REAL,
                attachment_path TEXT,
                start_date TEXT,
                end_date TEXT,
                FOREIGN KEY (enrollment_id) REFERENCES student_registry(enrollment_id)
            )
        ''')


        # --- Table 4: Faculty Registry ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faculty_registry (
                faculty_id TEXT PRIMARY KEY,
                faculty_name TEXT NOT NULL,
                password_key TEXT NOT NULL,
                assigned_subject_code TEXT,
                assigned_subject_name TEXT,
                faculty_email TEXT DEFAULT ''
            )
        ''')

        # --- Table 5: Attendance Ledger ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enrollment_id TEXT NOT NULL,
                subject_code TEXT,
                date_stamped DATE,
                scan_timestamp DATETIME
            )
        ''')

        # --- Table 6: Broadcast Notices ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broadcast_notices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_code TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # --- Pre-populate faculty registry ---
        faculty_seeds = [
            ("ski@6767", "Prof. Skibidi Saxena", "33556677", "CSE1101", "Computer Programming using C", "mayacahmadfaisa@gmail.com"),
            ("riz@1234", "Dr. Rizzler Rastogi", "Rizz@2026", "MTH1801", "Calculus for Engineers", "hoxfr88@gmail.com"),
            ("gya@9876", "Prof. Kai Fanat", "Fanat@9876", "COM1101", "Communication and Writing Skills", "aralhawsawi@gmail.com"),
            ("sig@4567", "Dr. Duke Jhatka", "Duke@4567", "MEC1101", "Elements of Mechanical Engineering", "mwhubroo@gmail.com")
        ]

        for f in faculty_seeds:
            cursor.execute('INSERT OR IGNORE INTO faculty_registry (faculty_id, faculty_name, password_key, assigned_subject_code, assigned_subject_name, faculty_email) VALUES (?, ?, ?, ?, ?, ?)', f)

        # --- Pre-populate student registry ---

        real_student_roster = [
            ("260331", "Ashna Goyal",     "Ashna@260331",   "kayceebukstein@gmail.com"),
            ("260281", "Akkshay Pandey",  "Akkshay@260281", "lolg88878@gmail.com"),
            ("260718", "Rohit Sharma",    "Rohit@260718",   "pitbullgators5@gmail.com"),
            ("260307", "Anurag Kumar",    "Anurag@260307",  "white13080@gmail.com"),
            ("260302", "Anshika Yadav",   "Anshika@260302", "alciraalvarez73@gmail.com"),
            ("260592", "Shivam Vella",    "Shivam@260592",  "shiva1.26cse@bmu.edu.in"),
            ("260260", "Aayush Anand",    "Aayush@260260",  "aayushanand000@gmail.com"),
        ]

        for eid, name, password, email in real_student_roster:
            cursor.execute('''
                INSERT OR IGNORE INTO student_registry
                (enrollment_id, student_name, password, email, conducted_lectures, attended_lectures, percentage)
                VALUES (?, ?, ?, ?, 0, 0, 0.0)
            ''', (eid, name, password, email))

        conn.commit()
    print("[SUBNETTX] Database initialized successfully.")


# =========================================
# TOKEN GENERATION ENGINE (HMAC-SHA256)
# =========================================
def get_current_time_block():
    return int(time.time() // TOKEN_ROTATION_SECONDS)


def generate_token(time_block_id):
    message = f"BLOCK:{time_block_id}".encode('utf-8')
    signature = hmac.new(SECRET_ROOM_SALT, message, hashlib.sha256).hexdigest().upper()
    return signature[:6]


def get_seconds_remaining():
    elapsed = time.time() % TOKEN_ROTATION_SECONDS
    return round(TOKEN_ROTATION_SECONDS - elapsed, 2)


# =========================================
# ROUTES
# =========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('index.html')

# CREATED TO PRESERVE PROFESSOR DASHBOARD (Since it shared the index.html route)
@app.route('/professor_dashboard')
def professor_dashboard():
    return render_template('index.html')


@app.route("/profile")
def render_profile_page():
    return render_template("profile.html")


# -----------------------------------------
# GET /api/get_token
# -----------------------------------------
@app.route('/api/get_token', methods=['GET'])
def api_get_token():
    block_id = get_current_time_block()
    token = generate_token(block_id)
    remaining = get_seconds_remaining()
    freq = get_ultrasonic_freq(block_id)
    return jsonify({
        "status": "active",
        "token": token,
        "current_token": token,
        "time_block_id": block_id,
        "seconds_remaining_in_block": remaining,
        "ultrasonic_freq": freq,
        "levc_active": LEVC_STATE["active"],
        "levc_color": LEVC_STATE["color"] if LEVC_STATE["active"] else None
    })


# -----------------------------------------
# POST /api/levc/trigger  (Professor fires a strobe event)
# -----------------------------------------
@app.route('/api/levc/trigger', methods=['POST'])
def api_levc_trigger():
    global LEVC_STATE
    color = random.choice(LEVC_COLORS)
    LEVC_STATE = {
        "active": True,
        "color": color,
        "issued_at": time.time(),
        "block_id": get_current_time_block()
    }
    print(f"[LEVC] Strobe event fired: {color} at {LEVC_STATE['issued_at']}")
    # Auto-expire after TTL
    def expire():
        import time
        time.sleep(LEVC_TTL_MS / 1000.0 + 0.5)
        LEVC_STATE["active"] = False
        print(f"[LEVC] Strobe window expired.")
    threading.Thread(target=expire, daemon=True).start()
    return jsonify({"success": True, "color": color, "ttl_ms": LEVC_TTL_MS})


# -----------------------------------------
# POST /api/levc/respond  (Student taps a color button)
# -----------------------------------------
@app.route('/api/levc/respond', methods=['POST'])
def api_levc_respond():
    data = request.get_json() or {}
    enrollment_id = data.get("enrollment_id", "").strip().upper()
    chosen_color = data.get("color", "").strip().upper()
    
    elapsed_ms = (time.time() - LEVC_STATE["issued_at"]) * 1000
    
    if elapsed_ms > LEVC_TTL_MS:
        return jsonify({"success": False, "error": "LEVC_EXPIRED", "detail": f"Response arrived at {elapsed_ms:.0f}ms — TTL window ({LEVC_TTL_MS}ms) already closed. Likely remote stream delay."}), 403
    
    if chosen_color != LEVC_STATE.get("color", ""):
        return jsonify({"success": False, "error": "LEVC_WRONG_COLOR", "detail": "Color mismatch. The student did not see the physical flash."}), 403
    
    return jsonify({"success": True, "detail": f"LEVC passed in {elapsed_ms:.0f}ms. Physical presence confirmed.", "elapsed_ms": elapsed_ms})


# -----------------------------------------
# POST /api/verify_attendance
# -----------------------------------------
@app.route('/api/verify_attendance', methods=['POST'])
def api_verify_attendance():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload received."}), 400

        enrollment_id = data.get('enrollment_id', '').strip().upper()
        submitted_token = data.get('token', '').strip().upper()
        submitted_pass = data.get('password', '').strip()
        subject_code = data.get('subject_code', '').strip().upper()
        client_timestamp = data.get('client_timestamp', 0)

        if not enrollment_id or not submitted_token:
            return jsonify({"error": "Missing enrollment_id or token."}), 400

        # LOGIN GATE
        if submitted_token == "LOGIN_ONLY" or submitted_pass != "":
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
            
                # Faculty check
                fac = conn.execute("SELECT * FROM faculty_registry WHERE upper(faculty_id) = ?", (enrollment_id,)).fetchone()
                if fac and fac["password_key"] == submitted_pass:
                    return jsonify({
                        "success": True, 
                        "role": "faculty", 
                        "message": f"Welcome {fac['faculty_name']}",
                        "faculty_name": fac['faculty_name'],
                        "subject_code": fac['assigned_subject_code'],
                        "subject_name": fac['assigned_subject_name']
                    })
                
                # Student check
                row = conn.execute("SELECT password FROM student_registry WHERE enrollment_id = ?", (enrollment_id,)).fetchone()

            if row and row[0] == submitted_pass:
                return jsonify({"success": True, "role": "student", "message": "Authentication gate clear."})
            return jsonify({"success": False, "error": "Invalid Credentials"}), 401

        # NORMAL TOKEN VERIFICATION
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")

            student = conn.execute("SELECT * FROM student_registry WHERE enrollment_id = ?", (enrollment_id,)).fetchone()
            if not student:
                return jsonify({"error": f"Enrollment ID '{enrollment_id}' not found."}), 403

            current_block = get_current_time_block()
            expected_current = generate_token(current_block)
            expected_previous = generate_token(current_block - 1)

            server_ts = time.time()
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or '127.0.0.1'
            latency_delta = abs(server_ts - float(client_timestamp)) * 1000 if client_timestamp else 9999

            # Fetch network profile
            net_profile = conn.execute("SELECT * FROM network_profiles WHERE network_id = 'L_HALL_AP'").fetchone()
            authorized_prefix = net_profile["segment_prefix"] if net_profile else '10.7.'
            max_latency = net_profile["maximum_allowed_latency_ms"] if net_profile else 150

            status = 'FLAGGED'
            detail = ''
            network_type = ''

            if client_ip != "127.0.0.1" and not client_ip.startswith(authorized_prefix) and not client_ip.startswith(ACTIVE_GATEWAY_SEGMENT):
                status = 'FLAGGED'
                detail = f'⚠️ FLAGGED: Hostel Subnet Outlier'
                network_type = 'OUTLIER'
            elif latency_delta > max_latency and client_ip != "127.0.0.1":
                status = 'FLAGGED'
                detail = f'⚠️ FLAGGED: Heavy Latency Relay Delay (>{latency_delta/1000:.1f}s)'
                network_type = 'RELAY'
            elif submitted_token not in [expected_current, expected_previous]:
                status = 'FLAGGED'
                detail = f'Token mismatch. Client delta: {latency_delta:.0f}ms.'
                network_type = 'INVALID'
            else:
                # Token matched — now check proximity vectors
                submitted_freq = data.get('detected_freq', 0)
                proximity_mode = data.get('proximity_mode', 'none')
                expected_freq = get_ultrasonic_freq(current_block)
                freq_tolerance = 150  # Hz tolerance for FFT bin resolution
            
                if proximity_mode == 'ultrasonic' and submitted_freq:
                    if abs(int(submitted_freq) - expected_freq) <= freq_tolerance:
                        status = 'VERIFIED'
                        detail = f'Token + Ultrasonic frequency matched ({submitted_freq}Hz ≈ {expected_freq}Hz). Physical presence confirmed.'
                        network_type = 'CLASSROOM'
                    else:
                        status = 'FLAGGED'
                        detail = f'⚠️ FLAGGED: Ultrasonic mismatch. Expected ~{expected_freq}Hz, got {submitted_freq}Hz. Likely remote stream (VoIP codec strips >15kHz).'
                        network_type = 'STREAM_PROXY'
                elif proximity_mode == 'levc_passed':
                    status = 'VERIFIED'
                    detail = f'Token + LEVC visual challenge passed. Physical presence confirmed.'
                    network_type = 'CLASSROOM'
                else:
                    status = 'VERIFIED'
                    detail = f'Token matched.'
                    network_type = 'CLASSROOM'

            conn.execute('''
                INSERT INTO verification_logs
                (enrollment_id, token_submitted, expected_token, time_block_id, client_timestamp, server_timestamp, status, detail, source_ip, network_type, recorded_latency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (enrollment_id, submitted_token, expected_current, current_block, client_timestamp, server_ts, status, detail, client_ip, network_type, latency_delta))

            if status == 'FLAGGED':
                threading.Thread(target=send_async_email_worker, args=(
                    SENDER_EMAIL,
                    "🚨 SUBNETTX INTEL FRAUD WARNING",
                    f"🚨 SUBNETTX INTEL FRAUD WARNING: Relational network anomaly isolated. Student Roll {enrollment_id} has been quarantined on the Faculty Threat Matrix for attempting an unauthorized proxy attendance injection via an outlying hostel router prefix/cellular tunnel."
                )).start()

            if status == 'VERIFIED':
                conn.execute('''
                    UPDATE student_registry
                    SET attended_lectures = attended_lectures + 1,
                        percentage = ROUND(CAST(attended_lectures + 1 AS REAL) / CASE WHEN conducted_lectures > 0 THEN conducted_lectures ELSE 1 END * 100, 2)
                    WHERE enrollment_id = ?
                ''', (enrollment_id,))
            
                conn.execute('''
                    INSERT INTO attendance_ledger (enrollment_id, subject_code, date_stamped, scan_timestamp, source_ip, network_type, recorded_latency, tracking_status, qr_token, detected_freq, levc_color)
                    VALUES (?, ?, CURRENT_DATE, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?)
                ''', (enrollment_id, subject_code, client_ip, network_type, latency_delta, status, submitted_token, submitted_freq, LEVC_STATE.get("color", "N/A") if proximity_mode == 'levc_fallback' or proximity_mode == 'levc_passed' else None))
                print(f"🔥 [LEDGER SECURED] Student {enrollment_id} verified present for course {subject_code} at real-time timestamp.")
            else:
                return jsonify({"error": detail, "status": "FLAGGED", "latency": latency_delta}), 403

            conn.commit()

        if status == 'VERIFIED':
            return jsonify({"success": True, "status": "VERIFIED", "message": f"Attendance logged for {enrollment_id}.", "detail": detail}), 200
        else:
            return jsonify({"status": "FLAGGED", "error": "Token verification failed.", "detail": detail}), 401



    # -----------------------------------------
    # GET /api/get_latest_notices
    # -----------------------------------------
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"CRASH: {str(e)}"}), 200

@app.route('/api/get_latest_notices', methods=['GET'])
def api_get_latest_notices():
    subject_code = request.args.get('subject_code', '').strip().upper()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        
        query = """
            SELECT id, subject_code, message, strftime('%Y-%m-%d %H:%M:%S', timestamp, 'localtime') as ts
            FROM broadcast_notices
            ORDER BY id DESC LIMIT 5
        """
        rows = conn.execute(query).fetchall()
        
    return jsonify({
        "success": True,
        "notices": [{"id": r["id"], "subject_code": r["subject_code"], "message": r["message"], "timestamp": r["ts"]} for r in rows]
    })


# -----------------------------------------
# GET /api/get_live_logs
# -----------------------------------------
@app.route('/api/get_live_logs', methods=['GET'])
def api_get_live_logs():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        rows = conn.execute('''
            SELECT enrollment_id, token_submitted, expected_token, time_block_id,
                   client_timestamp, server_timestamp, status, detail
            FROM verification_logs ORDER BY id DESC LIMIT 200
        ''').fetchall()

    logs = []
    seen_enrollments = set()
    for row in rows:
        enroll_id = row["enrollment_id"]
        # Deduplication filter: Only keep the most recent event per student
        if enroll_id not in seen_enrollments:
            seen_enrollments.add(enroll_id)
            logs.append({
                "type": "VALID" if row["status"] == "VERIFIED" else "FLAGGED",
                "enrollment_id": enroll_id,
                "token_submitted": row["token_submitted"],
                "expected_token": row["expected_token"],
                "time_block_id": row["time_block_id"],
                "timestamp": datetime.fromtimestamp(row["server_timestamp"]).strftime("%H:%M:%S") if row["server_timestamp"] else "",
                "status": row["status"],
                "detail": row["detail"],
                "flagged": row["status"] == "FLAGGED"
            })
    return jsonify({"logs": logs})


# -----------------------------------------
# GET /api/get_live_tickets
# -----------------------------------------
@app.route('/api/get_live_tickets', methods=['GET'])
def api_get_live_tickets():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        rows = conn.execute('''
            SELECT lt.id, lt.enrollment_id, lt.ticket_type, lt.reason, lt.status, lt.submitted_at, lt.attachment_path,
                   lt.start_date, lt.end_date, sr.student_name, sr.email
            FROM leave_tickets lt
            LEFT JOIN student_registry sr ON lt.enrollment_id = sr.enrollment_id
            WHERE lt.status = 'PENDING'
            ORDER BY lt.id DESC LIMIT 50
        ''').fetchall()

    tickets = []
    for row in rows:
        tickets.append({
            "id": row["id"],
            "enrollment_id": row["enrollment_id"],
            "student_name": row["student_name"] or "Unknown",
            "email": row["email"] or "",
            "ticket_type": row["ticket_type"],
            "reason": row["reason"],
            "status": row["status"],
            "attachment_path": row["attachment_path"],
            "start_date": row["start_date"],
            "end_date": row["end_date"]
        })
    return jsonify({"tickets": tickets})


# -----------------------------------------
# GET /api/query_student
# -----------------------------------------
@app.route('/api/query_student', methods=['GET'])
def api_query_student():
    enrollment_id = request.args.get('enrollment_id', '').strip().upper()
    if not enrollment_id:
        return jsonify({"success": False, "error": "Missing enrollment_id parameter."}), 400

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        student = conn.execute("SELECT * FROM student_registry WHERE enrollment_id = ?", (enrollment_id,)).fetchone()

    if not student:
        return jsonify({"success": False, "error": f"Student '{enrollment_id}' not found."}), 404

    return jsonify({
        "success": True,
        "student": {
            "enrollment_id": student["enrollment_id"],
            "student_name": student["student_name"],
            "email": student["email"],
            "conducted_lectures": student["conducted_lectures"],
            "attended_lectures": student["attended_lectures"],
            "percentage": student["percentage"]
        }
    })


# -----------------------------------------
# POST /api/commit_override
# -----------------------------------------
@app.route('/api/commit_override', methods=['POST'])
def api_commit_override():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload received."}), 400

    enrollment_id = data.get('enrollment_id', '').strip().upper()
    conducted = data.get('conducted')
    attended = data.get('attended')

    if not enrollment_id:
        return jsonify({"error": "Missing enrollment_id."}), 400
    if conducted is None or attended is None:
        return jsonify({"error": "Missing conducted or attended values."}), 400

    try:
        conducted = int(conducted)
        attended = int(attended)
    except (ValueError, TypeError):
        return jsonify({"error": "conducted and attended must be integers."}), 400

    if conducted < 0 or attended < 0:
        return jsonify({"error": "Values cannot be negative."}), 400
    if attended > conducted:
        return jsonify({"error": "Attended cannot exceed conducted."}), 400

    pct = round((attended / conducted) * 100, 2) if conducted > 0 else 0.0

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        student = conn.execute("SELECT * FROM student_registry WHERE enrollment_id = ?", (enrollment_id,)).fetchone()
        if not student:
            return jsonify({"error": f"Student '{enrollment_id}' not found."}), 404
        conn.execute('UPDATE student_registry SET conducted_lectures = ?, attended_lectures = ?, percentage = ? WHERE enrollment_id = ?',
                      (conducted, attended, pct, enrollment_id))
        conn.commit()

    return jsonify({"success": True, "message": f"Override committed for {enrollment_id}.", "updated": {"enrollment_id": enrollment_id, "conducted_lectures": conducted, "attended_lectures": attended, "percentage": pct}})


# -----------------------------------------
# POST /api/user/save_profile
# -----------------------------------------
@app.route("/api/user/save_profile", methods=["POST"])
def save_user_profile():
    payload = request.get_json() or {}
    uid = payload.get("enrollment_id", "").strip()
    name = payload.get("fullname", "").strip()
    email = payload.get("email", "").strip()

    if not uid or not name or not email:
        return jsonify({"success": False, "message": "Missing mandatory profile entries."}), 400

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM student_registry WHERE enrollment_id = ?", (uid,))
        exists = cursor.fetchone()[0]
        if exists > 0:
            cursor.execute("UPDATE student_registry SET student_name = ?, email = ? WHERE enrollment_id = ?", (name, email, uid))
        else:
            default_pwd = f"{name.split()[0]}@{uid}"
            cursor.execute("INSERT INTO student_registry (enrollment_id, student_name, password, email) VALUES (?, ?, ?, ?)", (uid, name, default_pwd, email))
        conn.commit()

    print(f"[PROFILE] UPDATE: ID: {uid} | Name: {name} | Email: {email}")
    return jsonify({"success": True, "message": "Profile synced successfully."})


# -----------------------------------------
# POST /api/professor/cancel_class
# -----------------------------------------
@app.route("/api/professor/cancel_class", methods=["POST"])
def professor_cancel_class():
    payload = request.get_json() or {}
    subject_code = payload.get("subject_code", "").strip()
    cancel_date = payload.get("date", "").strip()

    subject = f"CLASS CANCELLATION NOTICE: {subject_code} on {cancel_date}"
    body = f"Dear Student,\n\nThe lecture session for {subject_code} scheduled on {cancel_date} stands cancelled per faculty instructions.\n\nRegards,\nSubnettX Engine"

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        
        # 1. Insert into Live Notices table
        conn.execute("INSERT INTO broadcast_notices (subject_code, message, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)", (subject_code, body))
        
        # 2. Fetch emails for background SMTP delivery
        students = conn.execute("""
            SELECT DISTINCT student_registry.email
            FROM student_registry
            JOIN attendance_ledger ON student_registry.enrollment_id = attendance_ledger.enrollment_id
            WHERE attendance_ledger.subject_code = ? AND student_registry.email != ''
        """, (subject_code,)).fetchall()
        
        conn.commit()

    for (s_email,) in students:
        threading.Thread(target=send_async_email_worker, args=(s_email, subject, body)).start()

    return jsonify({"success": True, "message": "Broadcast cancellation notice emailed and posted to live dashboards."})


# -----------------------------------------
# POST /api/professor/resolve_ticket
# -----------------------------------------
@app.route("/api/professor/resolve_ticket", methods=["POST"])
def professor_resolve_ticket():
    payload = request.get_json() or {}
    enrollment_id = payload.get("enrollment_id", "").strip()
    ticket_id = payload.get("ticket_id", None)
    action = payload.get("action", "approve").lower()

    if action not in ["approve", "decline"]:
        return jsonify({"success": False, "error": "Invalid action."}), 400

    new_status = 'APPROVED' if action == 'approve' else 'DECLINED'

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        if ticket_id:
            conn.execute("UPDATE leave_tickets SET status = ?, reviewed_at = ? WHERE id = ?", (new_status, time.time(), ticket_id))
        row = conn.execute("SELECT email FROM student_registry WHERE enrollment_id = ?", (enrollment_id,)).fetchone()
        conn.commit()

    target_email = row[0] if (row and row[0]) else f"{enrollment_id}@university.edu"
    
    if action == 'approve':
        subject = "SUBNETTX: Leave Ticket APPROVED"
        body = "✅ SUBNETTX LIFE-CYCLE NOTICE: Your academic leave application document has been officially APPROVED by your coordinator professor. Relational ledger metrics successfully updated."
    else:
        subject = "SUBNETTX: Leave Ticket DECLINED"
        body = "❌ SUBNETTX LIFE-CYCLE NOTICE: Your academic leave application document has been DECLINED by your coordinator professor. You are expected to attend the sessions as scheduled."

    threading.Thread(target=send_async_email_worker, args=(target_email, subject, body)).start()

    return jsonify({"success": True, "status": new_status})


# -----------------------------------------
# POST /api/student/submit_ticket
# -----------------------------------------
@app.route("/api/student/submit_ticket", methods=["POST"])
def student_submit_ticket():
    # Support both FormData (files) and JSON payloads
    if request.content_type and 'multipart/form-data' in request.content_type:
        enrollment_id = request.form.get("enrollment_id", "").strip()
        ticket_type = request.form.get("ticket_type", "MEDICAL").strip()
        reason = request.form.get("reason", "").strip()
        student_email = request.form.get("student_email", "").strip()
        target_prof_id = request.form.get("assigned_prof", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        file = request.files.get("attachment")
    else:
        payload = request.get_json() or {}
        enrollment_id = payload.get("enrollment_id", "").strip()
        ticket_type = payload.get("ticket_type", "MEDICAL").strip()
        reason = payload.get("reason", "").strip()
        student_email = payload.get("student_email", "").strip()
        target_prof_id = payload.get("assigned_prof", "").strip()
        start_date = payload.get("start_date", "").strip()
        end_date = payload.get("end_date", "").strip()
        file = None

    saved_path = None
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"
        file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
        saved_path = unique_filename

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        if student_email:
            conn.execute("UPDATE student_registry SET email = ? WHERE enrollment_id = ?", (student_email, enrollment_id))
        
        conn.execute("INSERT INTO leave_tickets (enrollment_id, ticket_type, reason, status, submitted_at, attachment_path, start_date, end_date) VALUES (?, ?, ?, 'PENDING', ?, ?, ?, ?)",
                      (enrollment_id, ticket_type, reason, time.time(), saved_path, start_date, end_date))
        
        prof_row = conn.execute("SELECT faculty_email FROM faculty_registry WHERE faculty_id = ?", (target_prof_id,)).fetchone()
        conn.commit()

    prof_email = prof_row[0] if (prof_row and prof_row[0]) else None

    if prof_email:
        threading.Thread(target=send_async_email_worker, args=(
            prof_email,
            f"SUBNETTX LEAVE TICKET: Roll {enrollment_id}",
            f"SUBNETTX ACTION REQUIRED: Student Roll {enrollment_id} has filed an urgent {ticket_type} leave application request inside your room module queue.\nReason: {reason}\nReview the ticket parameters on your dashboard interface control panel."
        )).start()

    return jsonify({"success": True, "message": "Leave request submitted. Professor notified."})



# -----------------------------------------
# GET /api/attachments/<filename>
# -----------------------------------------
@app.route("/api/attachments/<filename>")
def serve_attachment(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# =========================================
# SERVER BOOT
# =========================================
if __name__ == '__main__':
    print("=" * 50)
    print("  SUBNETTX BACKEND SERVER")
    print("  Initializing secure attendance engine...")
    print("=" * 50)
    init_db()
    print(f"[SUBNETTX] Token rotation: every {TOKEN_ROTATION_SECONDS}s (HMAC-SHA256)")
    print(f"[SUBNETTX] Database path: {DB_PATH}")
    print("[SUBNETTX] Server launching on http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5000)
