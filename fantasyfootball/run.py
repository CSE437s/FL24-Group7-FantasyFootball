# /run.py

from flask import render_template
from app import create_app


# Load environment variables
app = create_app()


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=3000, ssl_context=("cert.pem", "key.pem"))
