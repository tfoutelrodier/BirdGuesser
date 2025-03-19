# Main file
# Run using python BirdGuesser/flaskr/app.py

from flask import Flask, render_template

# Import blueprints
from landing import landing_bp
from game import game_bp
from training import training_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(landing_bp)
app.register_blueprint(game_bp, url_prefix='/game')
app.register_blueprint(training_bp, url_prefix='/training')

if __name__ == '__main__':
    app.run(debug=True)