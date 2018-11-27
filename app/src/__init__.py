"""
Postman collection: https://www.getpostman.com/collections/0b5d7afae1db013baf80
"""

from flask import Flask, request, jsonify, session

from src.db import get_modelinfo_db
from src.db import get_feedback_db
from src import constants
from src.model import ModelInfo
from src.exceptions import InvalidDataError, ModelException
from src.utils import allowed_files


import os, json

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('instance.appconfig')
app.secret_key = app.config['SECRET_KEY']
# conn = get_db('RedisDB')
model_conn = get_modelinfo_db('CouchModelInfo', user=app.config['DB_USER'], password=app.config['DB_PASS'])
feedback_conn = get_feedback_db('CouchFeedback', user=app.config['DB_USER'], password=app.config['DB_PASS'])

# db.init_app(app)
#TODO: fix app init
#  turned this off because "in do_teardown_appcontext
#  TypeError: close_db() takes 0 positional arguments but 1 was given""


@app.route("/")
def main():
    return "Hello, world!"


@app.route("/model", methods=["PUT", "GET"])
def all_models():
    if request.method == "GET":
        limit = int(request.args.get('limit'))
        if not limit:
            limit = 10  # default
        try:
            result_list = model_conn.find_all_model_info(limit=limit)
            return jsonify(result_list), 200
        except Exception as e:
            return jsonify(str(e)), 500
    else:
        if request.is_json:
            data = request.get_json()
            model_info = ModelInfo(data['description'], data['metrics'], data['location'])
            try:
                # todo: fix how we store a dict of metrics
                model_conn.store_model_info(model_info.hash, model_info.items)
            except Exception as e:
                return jsonify(str(e)), 500
            return jsonify(model_info.hash), 201
        else:
            return jsonify("Request is not in JSON"), 500


@app.route("/model/<model_id>", methods=['GET'])
def model_info(model_id):
    """
    GET /model/<model_id> returns all info about <model_id>
    UNIMPLEMENTED (need to separate model serving from this app) :
    PUT /model/<model_id>?live=true makes a model "live" i.e. currently serving
    Body of this POST must be of {"input" : <text>} format

    :param model_id:
    :return:
    """
    if request.method == "GET":
        try:
            info_dict = model_conn.find_model_info(model_id)
            if info_dict:
                return jsonify(info_dict), 200
            else:
                return jsonify("Model Id {0} not found".format(model_id)), 404
        except:
            # DB call error, not ID error
            return jsonify("Internal error"), 500


    # is_live = request.args.get('live', None)   # look for liveness check
    # if is_live:
    #     info_dict = conn.find(model_id)
    #     info_dict['live'] = is_live
    #     conn.store(info_dict['hash'], info_dict)
    #     # todo: how to pass the model type here? needs to be from model info
    #     get_model('FastTextModel', info_dict['location'], 'MinioLoader')
    #     return jsonify(model_id), 204  # model was set live successfully
    # return jsonify('No liveness value specified'), 204


@app.route("/model/<model_id>/prediction", methods=['POST'])
def model_predict(model_id):
    """
    POST /model/<model_id>/prediction asks for a new prediction from
    this specific model.
    The format of the input request is:
    {
      "input" : "sample text to classify"
    }
    :param model_id: ID of model stored in model info entry
    :return:
    """
    try:
        info_dict = model_conn.find_model_info(model_id)
        model = get_modelinfo_db('FastTextModel', info_dict['location'], 'MinioLoader')\
            .load(app.instance_path)
        if model is None:
            raise ModelException(
                'Model could not be found at path: {}'.format(app.instance_path))
    except Exception as e:
        return jsonify(str(e)), 500
    try:
        to_predict = json.loads(request.data.decode('utf-8'))['input']
    except Exception as e:
        return jsonify('Could not load input as JSON: ' + str(e))
    prediction = model.predict(to_predict)
    result = {'label' : prediction[0][0], 'score' : prediction[1][0]}
    return jsonify(result)


@app.route("/feedback", methods=['GET', 'PUT'])
def get_feedback():
    if request.method == 'GET':
        model_id = request.args.get('model_id')
        limit = request.args.get('limit')
        if not limit:
            limit = 10
        else:
            limit = int(limit)
        try:
            if model_id:
                results = feedback_conn.get_feedback(model_id, limit)
            else:
                results = feedback_conn.get_feedback(None, limit)
            return jsonify(results),200
        except Exception as e:
            jsonify(str(e)), 500
    else:
        feedback = request.get_json()
        try:
            fb_id = feedback_conn.store_feedback(feedback)
            return jsonify(fb_id), 201
        except Exception as e:
            return jsonify(str(e)), 500

if __name__ == "__main__":
    # make sure the instance path is present
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.run(debug=1)