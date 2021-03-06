from flask import current_app, g
import pymongo


def get_db():
    if 'db' not in g:
        g.db = pymongo.MongoClient('localhost', 27017)

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(flask_app):
    flask_app.teardown_appcontext(close_db)
