from flask import Flask
from flask import render_template

# Create a Flask application instance
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


# Run the Flask server only if this script is executed directly
def run(host="127.0.0.1", port=5000, debug=True):
    # host="127.0.0.1" (default) means local only
    # debug=True enables auto-reload for development
    # port=5000 is default Flask port
    app.run(host="127.0.0.1", port=5000, debug=True)
