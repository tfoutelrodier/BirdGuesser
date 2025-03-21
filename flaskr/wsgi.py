import os
import sys

# Add the root directory to the Python module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import app

# WSGI entry point for the Flask app
if __name__ != "__main__":
    application = app
