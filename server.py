from flask import Flask
import sys


def create_app(test_config=None):
    app = Flask(__name__)

    import storage_app.db as db
    db.init_app(app)

    import storage_app.simplywallst_api as simplywallst_api
    app.register_blueprint(simplywallst_api.bp)

    import flask

    # test route
    @app.route('/')
    def home():
        exmpl_url = flask.request.host_url + "simplywallst/AAPL"
        return f"example request:<br><a href=\"{exmpl_url}\">{exmpl_url}</a>"

    return app
