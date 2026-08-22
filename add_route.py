import os

app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
with open(app_path, 'r', encoding='utf-8') as f:
    app_code = f.read()

route_code = """
@app.route('/maitri_portal')
def maitri_portal():
    return render_template('maitri_portal.html')
"""

if "def maitri_portal():" not in app_code:
    # insert before if __name__ == '__main__':
    idx = app_code.rfind("if __name__ == '__main__':")
    if idx != -1:
        app_code = app_code[:idx] + route_code + "\n" + app_code[idx:]
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(app_code)
        print("Route added to app.py")
    else:
        print("Could not find __main__ block")
else:
    print("Route already exists")
