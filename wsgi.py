import os
import sys
import pathlib

# Add the project root to the Python path to be secure
root_path = pathlib.Path(__file__).parent
sys.path.insert(0, str(root_path))

from flaskr import app

if __name__ == "__main__":
    app.run()
