#!/usr/bin/python3

import pickle
import numpy as np
import pandas as pd
from io import BytesIO
import xlsxwriter
from flask import Flask, request, make_response, send_file
import time
import zipfile

model = None
app = Flask(__name__)

with open('/var/www/html/web/iris_trained_model.pkl', 'rb') as mfile:
        model = pickle.load(mfile)

@app.route('/')
def home_endpoint():
    return 'Hello World!'

#####  ------   SAMPLE CODE   -----
##input=Direct arguments (Method=GET)
#@app.route('/predictg')
#def predict_iris():
#    s_length = request.args.get("s_length")
#    s_width = request.args.get("s_width")
#    p_length = request.args.get("p_length")
#    p_width = request.args.get("p_width")
#    prediction = model.predict(np.array([[s_length, s_width, p_length, p_width]]))
#    return str(prediction)

## Sample post method for reading arguments
#@app.route('/', methods=['POST'])
#def add():
#    a=request.form["a"]
#    b=request.form["b"]
#    return str(int(a) + int(b))

## Input=Direct_arguments Output=OnScreen
@app.route('/predict', methods=['POST'])
def get_prediction():
    if request.method == 'POST':
        data = request.get_json()             # Get data posted as a json
        data = np.array(data)[np.newaxis, :]  # converts shape from (4,) to (1, 4)
        prediction = model.predict(data)      # runs globally loaded model on the data
    return str(prediction[0])

## Input=CSV, Output=OnScreen
@app.route('/predict_file', methods=["POST"])
def predict_iris_file():
    input_data = pd.read_csv(request.files.get("input_file"), header=None)
    prediction = model.predict(input_data)
    return str(list(prediction))

## Input=CSV, Output=Excel
@app.route('/predict_file_o', methods=["POST"])
def predict_iris_fileo():

    input_data = pd.read_csv(request.files.get("input_file"), header=None)
    prediction = model.predict(input_data)
    dataset = pd.DataFrame({'output': prediction})
    input_data = input_data.join(dataset)

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    input_data.to_excel(writer, sheet_name='Clusters', encoding='utf-8', index=False)
    workbook = writer.book
    worksheet = writer.sheets["Clusters"]
    writer.close()
    output.seek(0)
    #finally return the file
    return send_file(output, attachment_filename="testing.xlsx", as_attachment=True)

## Input=CSV Output=Zipped_Excel_file
@app.route('/predict_file_oz', methods=["POST"])
def predict_iris_fileoz():

    input_data = pd.read_csv(request.files.get("input_file"), header=None)
    prediction = model.predict(input_data)
    dataset = pd.DataFrame({'output': prediction})
    input_data = input_data.join(dataset)

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    input_data.to_excel(writer, sheet_name='Clusters', encoding='utf-8', index=False)
    writer.save()

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
         names = ['cluster_output.xlsx']
         files = [output]
         for i in range(len(files)):
            input_data = zipfile.ZipInfo(names[i])
            input_data.date_time = time.localtime(time.time())[:6]
            input_data.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(input_data, files[i].getvalue())
    memory_file.seek(0)
    response = make_response(send_file(memory_file, attachment_filename='cluster_output.zip', as_attachment=True))
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response
