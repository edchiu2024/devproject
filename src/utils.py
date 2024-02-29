import os
import sys
import requests
from requests.auth import HTTPBasicAuth

import json
import dill
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV, cross_val_score
from exception import CustomException


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logging 
from exception import CustomException

def load_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'CONFIG.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def get_reddit_access_token():
    config = load_config()
    url = config['REDDIT']['AUTHENTICATION_API_URL']+"/access_token"
    refresh_token = config['REDDIT']['REFRESH_TOKEN']
    client_id = config['REDDIT']['CLIENT_ID']
    client_secret = config['REDDIT']['CLIENT_SECRET']
    UA = config['REDDIT']['UA']
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    headers = {
        'User-Agent': UA
    }
    auth = HTTPBasicAuth(client_id, client_secret)
    try:
        response = requests.post(url, data=data, auth=auth, headers=headers)
        access_token_data = response.json()
        return access_token_data['access_token']
    except Exception as e:
        raise CustomException(e, sys)
    
    

def save_object(file_path, obj):
    try:
        dir_path = os.path.dirname(file_path)

        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)

    except Exception as e:
        raise CustomException(e, sys)
    
def load_object(file_path):
    try:
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)

    except Exception as e:
        raise CustomException(e, sys)

def evaluate_models(X_train, y_train, X_test, y_test, models, param):
    report = {}
    for model_name, model in models.items():
        try:
            para = param[model_name]

            gs = GridSearchCV(model, para, cv=3)
            gs.fit(X_train, y_train)

            # Set the model to the best found parameters
            model.set_params(**gs.best_params_)
            model.fit(X_train, y_train)

            # Predictions
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            # Scoring
            train_model_score = r2_score(y_train, y_train_pred)
            test_model_score = r2_score(y_test, y_test_pred)
            # Cross-validation R^2 score
            cv_r2_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
            cv_r2_mean = np.mean(cv_r2_scores)

            # R^2 score is to check how well the model fits. 
            # High score could suggest it's overfitting.
            # It has nothing to do with accuracy/precision/recall 

            # We could also look at other metrics such as mean_absolute_error 
            # and mean_squared_error but we are only going to evaluate R2 in this project
            # This can be improved by looking at high R² score and balance between MAE and MSE

            #report[model_name] = test_model_score
            report[model_name] = cv_r2_mean     
            # Instead of using the test_model_score, we use the cross validation mean for generalization purposes 
            
        except Exception as e:
            # Handle or log the exception as needed
            report[model_name] = {'error': str(e)}
    
    return report

  