import os

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html_code = f.read()

start_marker = "<!-- TIME LOCK OVERLAY -->"
end_marker = "setTimeout(enforceTimeLock, 0);"

start_idx = html_code.find(start_marker)
end_idx = html_code.find(end_marker) + len(end_marker)

if start_idx != -1 and end_idx != -1:
    new_html = html_code[:start_idx] + "\n" + html_code[end_idx:]
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Time lock removed.")
else:
    print("Could not find markers.")
