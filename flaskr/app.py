# Main file
# Run using python BirdGuesser/flaskr/app.py

from flaskr import app

if __name__ == '__main__':
    # for local run
    # app.run(debug=True)
    # for vercel hosting
    app.run(host="0.0.0.0", port=8080, debug=True)