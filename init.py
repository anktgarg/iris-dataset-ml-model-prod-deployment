#!/usr/bin/python3

import pickle
import numpy as np
from flask import Flask, request

model = None
app = Flask(__name__)

with open('/var/www/html/web/iris_trained_model.pkl', 'rb') as mfile:
        model = pickle.load(mfile)


@app.route('/')
def home_endpoint():
    return 'Hello World!'

@app.route('/predict', methods=['POST'])
def get_prediction():
    # Works only for a single sample
    if request.method == 'POST':
        data = request.get_json()  # Get data posted as a json
        data = np.array(data)[np.newaxis, :]  # converts shape from (4,) to (1, 4)
        prediction = model.predict(data)  # runs globally loaded model on the data
    return str(prediction[0])

