# ETL job for Reddit interview
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


    def initiate_data_extract(self):
        logging.info("Entered the data extraction method")
        config = load_config()
        user_agent = config['REDDIT']['UA']
        trimmed_data_filename=config['REDDIT']['JSON_FILE_NAME']
        access_token = get_reddit_access_token()
        sub_reddit=['stocks','wallstreetbets','investing']
        #sub_reddit=['stocks']
        limit=10
        interval="day"
        today_date = datetime.now().strftime('%Y-%m-%d')

        headers = {
            'Authorization': 'Bearer '+access_token,
            'User-Agent': user_agent
        }     
        trimmed_data = []   
        for i, subR in enumerate(sub_reddit):
            try:
                logging.info(f"Making API call to fetch top posts from {subR} subreddit")
                response = requests.get(f'https://oauth.reddit.com/r/{subR}/top.json?limit={limit}&t={interval}', headers=headers)
                
                logging.info(f"Trimming data")
                response=response.json()
                for post in response['data']['children']:
                    logging.info(f"saving post")
                    post_data = post['data']
                    trimmed_post = {
                        'id': post_data['id'],  # Unique post ID
                        'subreddit': post_data['subreddit'],
                        'upload_date':today_date,
                        'title': post_data['title'],
                        'selftext': post_data['selftext'],
                        'created': datetime.utcfromtimestamp(post_data['created']).strftime('%Y-%m-%d'),
                        'num_comments': post_data['num_comments'],
                        'ups': post_data['ups'],
                        'downs': post_data['downs'], # Reddit typically shows 0 for this due to how they handle voting.
                        'score': post_data['score'],
                        'permalink': f"https://www.reddit.com{post_data['permalink']}"
                    }

                    trimmed_data.append(trimmed_post)
                    
                    

                    
            except Exception as e:
                logging.error(f"Error fetching data from Reddit: {e}")
                raise CustomException(e,sys)
            
        try:
            trimmed_data_path = os.path.join('../../artifacts', trimmed_data_filename)
            logging.info(f"Saving to a local json file")
            with open(trimmed_data_path, 'w') as outfile:
                json.dump(trimmed_data, outfile, indent=4)
            return trimmed_data_path
        except Exception as e:
            logging.error(f"Error saving file: {e}")
            raise CustomException(e,sys)        
        
if __name__=="__main__":
     

    obj=DataExtraction()
    print(obj.initiate_data_extract())

    #train_data,test_data=obj.initiate_data_ingestion()

    #data_transformation=DataTransformation()
    #train_arr,test_arr,_=data_transformation.initiate_data_transformation(train_data,test_data)

    #modeltrainer=ModelTrainer()
    #print(modeltrainer.initiate_model_trainer(train_arr, test_arr))