# ETL job for Reddit interview
from data_transformer import Transformer

import os
import json
import sys
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logging 
from exception import CustomException
from datetime import datetime
from utils import load_config,get_reddit_access_token

class DataExtraction:

  
    def post_data_extract(self):

        transformer = Transformer()

        data="EPS is listed as 0.09 on Yahoo, so that seems to be your gap. With that, 0.09 x 257 is about $21.7, which seems to line up. \n\nMaybe they issued a lot of stock recently, so the nominal EPS doesn\u2019t match what they actually paid out per share?"

            
            
        summarized_text=transformer.summarizer(data) 
        print(summarized_text)
 
if __name__=="__main__":
     

    obj=DataExtraction()
    obj.post_data_extract()

    #train_data,test_data=obj.initiate_data_ingestion()

    #data_transformation=DataTransformation()
    #train_arr,test_arr,_=data_transformation.initiate_data_transformation(train_data,test_data)

    #modeltrainer=ModelTrainer()
    #print(modeltrainer.initiate_model_trainer(train_arr, test_arr))