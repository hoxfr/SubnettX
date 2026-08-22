import os
import shutil

src_dir = r"E:\Downloads\new edit"
dst_dir = r"C:\Users\anurag\.gemini\antigravity\scratch\SubnettX"

# Copy profile.html (no maitri logic there)
shutil.copy(os.path.join(src_dir, 'profile.html'), os.path.join(dst_dir, 'templates', 'profile.html'))
print("profile.html copied.")

# Process app.py
with open(os.path.join(src_dir, 'app.py'), 'r', encoding='utf-8') as f:
    app_code = f.read()

maitri_route = """
@app.route('/maitri_portal')
def maitri_portal():
    return render_template('maitri_portal.html')
"""
if "/maitri_portal" not in app_code:
    idx = app_code.rfind("if __name__ == '__main__':")
    if idx != -1:
        app_code = app_code[:idx] + maitri_route + "\n" + app_code[idx:]
        
with open(os.path.join(dst_dir, 'app.py'), 'w', encoding='utf-8') as f:
    f.write(app_code)
print("app.py updated with Maitri route.")

# Process index.html
with open(os.path.join(dst_dir, 'templates', 'index.html'), 'r', encoding='utf-8') as f:
    old_index = f.read()

# Extract Maitri HTML from my current index
maitri_html_start = old_index.find("<!-- Maitri Sync Engine -->")
maitri_html_end = old_index.find("<!-- Right Column -->") - 21
maitri_html = old_index[maitri_html_start:maitri_html_end]

# Extract Maitri JS from my current index
maitri_js_start = old_index.find("/* =========================================\n           MAITRI SYNC ENGINE (DEMO)")
maitri_js_end = old_index.find("</script>\n</body>")
maitri_js = old_index[maitri_js_start:maitri_js_end]

with open(os.path.join(src_dir, 'index.html'), 'r', encoding='utf-8') as f:
    new_index = f.read()

# Inject Maitri HTML before Right Column
if maitri_html_start != -1 and "<!-- Maitri Sync Engine -->" not in new_index:
    new_index = new_index.replace("<!-- Right Column -->", maitri_html + "\n                    <!-- Right Column -->")

# Inject Maitri JS before closing script
if maitri_js_start != -1 and "generateMaitriReport" not in new_index:
    new_index = new_index.replace("</script>\n</body>", maitri_js + "\n    </script>\n</body>")
    new_index = new_index.replace("</script>\r\n</body>", maitri_js + "\n    </script>\r\n</body>")

with open(os.path.join(dst_dir, 'templates', 'index.html'), 'w', encoding='utf-8') as f:
    f.write(new_index)
print("index.html updated with Maitri components.")
