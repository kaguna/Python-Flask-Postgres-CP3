# runs the API
from flask import redirect

from app import create_app

app = create_app("development")

@app.route("/")
def home():
    return redirect("/apidocs")


if __name__ == '__main__':
    app.run()
