# TODO: use app creation factory and/or wsgi
# import os
#
# from flask import Flask, request
#
# # https://stackoverflow.com/questions/13751277/how-can-i-use-an-app-factory-in-flask-wsgi-servers-and-why-might-it-be-unsafe
#
# def __init_configs(app, test_config=None):
#     """
#     Init configs from file or variable
#     :param app:
#     :param test_config:
#     :return:
#     """
#     app.config.from_mapping(
#         SECRET_KEY="dev"
#     )
#     if test_config is None:
#         app.config.from_pyfile('config.py', silent=True)
#     else:
#         app.config.from_mapping(test_config)
#
#     # make sure the instance path is present
#     try:
#         os.makedirs(app.instance_path)
#     except OSError:
#         pass
#
#
# def __init_db(app):
#     """
#     Creates the DB connection and inits
#     the app teardown context
#     :param app:
#     :return:
#     """
#     from .db import get_db
#     from .db import init_app
#
#     init_app(app)
#     return get_db()
#
#
# def create_app(test_config=None):
#     app = Flask(__name__, instance_relative_config=True)
#     __init_configs(app, test_config)
#     db = __init_db(app)
#
#     @app.route("/")
#     def main():
#         return "Hello, world!"
#
#     @app.route("/model", methods=("POST", "GET"))
#     def model():
#         if request.method == "GET":
#             return db.smembers('models')
#
#     return app