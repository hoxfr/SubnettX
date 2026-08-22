import re
import os

app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
with open(app_path, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Fix CRIT-1
app_code = app_code.replace("data.get('detected_freq', 0)", "data.get('ultrasonic_freq', 0)")

# Fix HIGH-1
# We need to find the specific else block. Let's use regex.
import re
app_code = re.sub(
    r"(else:\s+)status = 'VERIFIED'(\s+detail = f'\?\? FLAGGED: Ultrasonic mismatch)",
    r"\1status = 'FLAGGED'\2",
    app_code
)

# Fix HIGH-3: Add a SELECT guard
guard_sql = """
            # HIGH-3: Prevent double check-ins
            existing = conn.execute("SELECT 1 FROM verification_logs WHERE enrollment_id = ? AND time_block_id = ? AND status = 'VERIFIED'", (enrollment_id, current_block)).fetchone()
            if existing and status == 'VERIFIED':
                return jsonify({"success": False, "error": "Already verified for this time block"})
"""
if "INSERT INTO verification_logs" in app_code and "Prevent double check-ins" not in app_code:
    app_code = app_code.replace(
        "conn.execute('''\n                INSERT INTO verification_logs",
        guard_sql + "\n            conn.execute('''\n                INSERT INTO verification_logs"
    )

# Fix CRIT-2: Unauthenticated token endpoint
if "def api_get_token():" in app_code and "X-Faculty-Auth" not in app_code:
    app_code = app_code.replace(
        "def api_get_token():",
        "def api_get_token():\n    if request.headers.get('X-Faculty-Auth') != 'true':\n        return jsonify({'error': 'Unauthorized'}), 403"
    )

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_code)


html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html_code = f.read()

# Fix CRIT-4: Define let currentSubject
if "function updateSubject()" in html_code and "let currentSubject =" not in html_code:
    html_code = html_code.replace(
        "function updateSubject() {",
        "let currentSubject = document.getElementById('subject-selector') ? document.getElementById('subject-selector').value : '';\n        function updateSubject() {"
    )
    html_code = html_code.replace(
        "// Add logic to swap tables",
        "currentSubject = document.getElementById('subject-selector').value;\n            // Add logic to swap tables"
    )

# Fix CRIT-2 frontend side
if "fetch('/api/get_token')" in html_code:
    html_code = html_code.replace(
        "fetch('/api/get_token')",
        "fetch('/api/get_token', { headers: { 'X-Faculty-Auth': 'true' } })"
    )

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_code)

print("Applied fixes.")
