from flask import Flask, jsonify
from playhouse.shortcuts import model_to_dict
from db.models import HealthCheckModel

app = Flask(__name__)


@app.route("/states")
def states():
	return jsonify(list(HealthCheckModel.select().dicts()))