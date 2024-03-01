# required file for AWS Elastic Beanstalk 
from flask import Flask,request,render_template ,send_from_directory 
from flask_cors import CORS
import sys
import numpy as np
import pandas as pd
from src.pipeline.predict_pipeline import CustomData, PredictPipeline
from src.pipeline.read_pipeline import ReadPipeline

from sklearn.preprocessing import StandardScaler
from src.exception import CustomException

application=Flask(__name__, static_folder='./react_build', static_url_path='/')
app=application  

CORS(app, resources={r"/api/*": {"origins": "https://edchiu.io"}})


## Route

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/members')
def members():
    return {"members":["Member1","Member2","Member3"]}

#def index():
#    return render_template('index.html')

@app.route('/reddit')
def reddit_read():
    read_pipeline=ReadPipeline()
    results=read_pipeline.read()
    return results

@app.route('/predictdata', methods=['GET','POST'])
def predict_datapoint():
    if request.method=='GET':
        return render_template('home.html')
    else:
        data=CustomData(
            gender=request.form.get('gender'),
            race_ethnicity=request.form.get('ethnicity'),
            parental_level_of_education=request.form.get('parental_level_of_education'),
            lunch=request.form.get('lunch'),
            test_preparation_course=request.form.get('test_preparation_course'),
            reading_score=float(request.form.get('writing_score')),
            writing_score=float(request.form.get('reading_score'))

        )
        
        pred_df=data.get_data_as_data_frame()
        predict_pipeline=PredictPipeline()
        results=predict_pipeline.predict(pred_df)
        
        #results is a list with just one value
        return render_template('home.html',results=results[0])
        

if __name__=="__main__":
    app.run(host="0.0.0.0")    
    

