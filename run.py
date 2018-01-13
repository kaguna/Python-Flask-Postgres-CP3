# runs the API
import os
from flask import redirect
from app import create_app

app = create_app(os.getenv('APP_SETTINGS'))


@app.route('/')
def rundoc():
    """method to run app documentation
    """
    return redirect('/apidocs/')


if __name__ == '__main__':
    app.run(port=5000)
