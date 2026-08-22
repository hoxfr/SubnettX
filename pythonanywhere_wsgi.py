import sys
import os

# 1. Add your project directory to the sys.path
# Replace 'yourusername' with your actual PythonAnywhere username!
project_home = '/home/yourusername/SubnettX'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# 2. Set the working directory so SQLite database paths resolve correctly
os.chdir(project_home)

# 3. Import the Flask app object
# (This imports 'app' from your app.py file)
from app import app as application

# PythonAnywhere will look for a variable named 'application' to run your WSGI server.
