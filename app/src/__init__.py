"""
Redis: ~/Git_personal/MachineLearning/gutenberg/redis-stable/src/redis-server
Minio: [start Docker] docker run -p 9000:9000 -e "MINIO_ACCESS_KEY=admin" -e "MINIO_SECRET_KEY=password" minio/minio server /data


Issues:
1. g variable is only request-specific. Cannot share data between requests.
2. Session is only used for user/browser data. Tested and showed that session
info between current Chrome browser and incognito is not shared.
3. Models could be too large to be passed around this way either.
4. And anyway models are not JSON serializable which means they cannot be stored
in the session object.

Technically, we need to spin up Docker containers to serve the models,
then have the models do some kind of sampling/reporting so that we can
record feedback.

But for now, we can load the models whenever we want a prediction.
When we want a prediction, we can specify which model to use and then
ask for a prediction.
Sending feedback to the DB can be done via model ID: input, model output,
expected output. Can do this with Redis also actually.

"""

from flask import Flask, request, jsonify, session

from src.altdb import get_modelinfo_db
from src.db import get_db
from src import constants
from src.model import ModelInfo
from src.exceptions import InvalidDataError, ModelException
from src.utils import allowed_files
from src.model import get_model

import os, json

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('instance.appconfig')
app.secret_key = app.config['SECRET_KEY']
# conn = get_db('RedisDB')
conn = get_modelinfo_db('CouchModelInfo', user=app.config['DB_USER'], password=app.config['DB_PASS'])

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
        resp = [x for x in conn.find_all_model_info(limit=15)]
        return jsonify(resp), 200
    else:
        if request.is_json:
            data = request.get_json()
            model_info = ModelInfo(data['description'], data['metrics'], data['location'])
            try:
                # todo: fix how we store a dict of metrics
                conn.store_model_info(model_info.hash, model_info.items)
            except Exception as e:
                return jsonify(str(e)), 500
            return jsonify(model_info.hash), 201
        else:
            return jsonify(InvalidDataError("request is not in JSON")), 500


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
        info_dict = conn.find_model_info(model_id)
        return jsonify(info_dict)

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
    info_dict = conn.find_model_info(model_id)
    model = get_model('FastTextModel', info_dict['location'], 'MinioLoader')\
        .load(app.instance_path)
    if model is None:
        raise ModelException(
            'Model could not be found at path: {}'.format(app.instance_path))
    try:
        to_predict = json.loads(request.data.decode('utf-8'))['input']
    except Exception as e:
        return jsonify('Could not load input as JSON: ' + str(e))
    prediction = model.predict(to_predict)
    result = {'label' : prediction[0][0], 'score' : prediction[1][0]}
    return jsonify(result)

if __name__ == "__main__":
    # make sure the instance path is present
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.run(debug=1)