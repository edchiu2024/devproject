import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logging 
from exception import CustomException
from utils import load_config



class ReadPipeline:
    def __init__(self):
        pass
    def read(self):
        config = load_config()
        filename=config['REDDIT']['JSON_FILE_NAME']
        try:
            file_path=os.path.join("artifacts",filename)
            with open(file_path, 'r') as file:
                # Load the JSON data from the file
                data = json.load(file)

            return data
        except Exception as e:
            raise   CustomException(e, sys)

