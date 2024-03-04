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

    def __init__(self):
        config = load_config()
        self.trimmed_data_filename=config['REDDIT']['JSON_FILE_NAME']
        self.sub_reddit=['stocks','wallstreetbets','investing']
        #self.sub_reddit=['stocks']
        self.today_date = datetime.now().strftime('%Y-%m-%d')
        self.post_limit=20
        self.post_interval="day"
        self.trimmed_data = [] 
        self.headers = {
            'Authorization': 'Bearer '+get_reddit_access_token(),
            'User-Agent': config['REDDIT']['UA'],
            'Accept': 'application/json'
        }    
    def post_data_extract(self):
        logging.info("Entered the post data extraction method") 
        transformer = Transformer()
        for i, subR in enumerate(self.sub_reddit):
            try:
                logging.info(f"Making API call to fetch top posts from {subR} subreddit")
                response = requests.get(f'https://oauth.reddit.com/r/{subR}/top?limit={self.post_limit}&t={self.post_interval}', headers=self.headers)
                
                logging.info(f"Trimming post data")
                response=response.json()


                for post in response['data']['children']:
                    logging.info(f"saving post")
                    post_data = post['data']
                    comments=self._comment_data_extract(post_data['id'],subR)
                    flattened_comments=self._flatten_comments(comments)
                    flattened_comments_string = '\n'.join(flattened_comments)
                    if flattened_comments_string:  # Check if there's any text to summarize
                        summarized_comments = transformer.summarize_text(flattened_comments_string)
                        if summarized_comments:  # Ensure there's a summarized text to analyze
                            comment_sentiments = transformer.analyze_sentiment(summarized_comments)
                            # Debugging: Log the output to inspect
                            logging.info(f"Comment Sentiments: {comment_sentiments}")
                            if comment_sentiments:
                                aggregated_label = comment_sentiments[0].get('label', 'Neutral')
                                aggregated_score = comment_sentiments[0].get('score', 0)
                            else:
                                aggregated_label = 'Neutral'
                                aggregated_score = 0
                    else:
                        aggregated_label = 'Neutral'
                        aggregated_score = 0

                    summarized_text=transformer.summarize_text(post_data['selftext']) if post_data['selftext'] else ''

                    trimmed_post = {
                        'id': post_data['id'],  # Unique post ID
                        'subreddit': post_data['subreddit'],
                        'upload_date':self.today_date,
                        'title': post_data['title'],
                        'selftext': post_data['selftext'],
                        'summarized_selftext': summarized_text,
                        'summarized_comments': summarized_comments,
                        'comment_sentiment':aggregated_label,
                        'comment_sentiment_confidence':aggregated_score,
                        'created': datetime.utcfromtimestamp(post_data['created']).strftime('%Y-%m-%d'),
                        'num_comments': post_data['num_comments'],
                        'ups': post_data['ups'],
                        'downs': post_data['downs'], 
                        'score': post_data['score'],
                        'permalink': f"https://www.reddit.com{post_data['permalink']}",
                        #'comments': comments
                        
                    }

                    self.trimmed_data.append(trimmed_post)
                    
                    

                    
            except Exception as e:
                logging.error(f"Error fetching data from Reddit: {e}")
                raise CustomException(e,sys)
            
        try:
            trimmed_data_path = os.path.join('../../artifacts', self.trimmed_data_filename)
            logging.info(f"Saving to a local json file")
            with open(trimmed_data_path, 'w') as outfile:
                json.dump(self.trimmed_data, outfile, indent=4)
            return trimmed_data_path
        except Exception as e:
            logging.error(f"Error saving file: {e}")
            raise CustomException(e,sys) 


    def _comment_data_extract(self,post_id, sub_reddit):
        logging.info("Entered the comment data extraction method") 

        try:
            logging.info(f"Making API call to fetch top posts from {sub_reddit} subreddit")
            response = requests.get(f'https://oauth.reddit.com/r/{sub_reddit}/comments/{post_id}', headers=self.headers)
            
            logging.info(f"Trimming comment data")
            response=response.json()[1]

            trimmed_comment_list=[]
            for comment in response['data']['children']:
                logging.info(f"Looping through comments for post {post_id}")
                comment_data = comment['data']
  
                trimmed_comment = {
                    'kind': comment.get('kind',''),
                    'id': comment_data['id'],  # Unique comment ID
                    'created': datetime.utcfromtimestamp(comment_data.get('created')).strftime('%Y-%m-%d') if ('created' in comment_data and comment_data['created']) else '',
                    'permalink': f"https://www.reddit.com{comment_data.get('permalink')}",
                    'ups': comment_data.get('ups', 0),
                    'score': comment_data.get('score', 0),
                    'body': comment_data.get('body', ''),
                    'replies': self._extract_replies(comment_data.get('replies', {}), comment_data['id'])  
                }
                trimmed_comment_list.append(trimmed_comment)
        except Exception as e:
            logging.error(f"Error fetching coomment data from post {post_id} from Reddit: {e}")
            raise CustomException(e,sys)
        return trimmed_comment_list              
        

    def _extract_replies(self, data, parent_id=None):
        processed_replies = []

        # Ensure data['replies'] contains actual reply data
        if isinstance(data, dict) and 'data' in data and 'children' in data['data']:
            for child in data['data']['children']:
                if child.get('kind') == 'more':  # Skip items with "kind" equal to "more"
                    continue                
                reply_data = child['data']
                reply_dict = {
                    'kind': child['kind'],
                    'id': reply_data['id'],
                    'parent_id': parent_id,  # Use the passed parent_id for the parent_id field
                    'permalink': f"https://www.reddit.com{reply_data.get('permalink')}",
                    'ups': reply_data.get('ups', 0),
                    'score': reply_data.get('score', 0),
                    'body': reply_data.get('body', '')
                }

                # Recursively process further replies
                if 'replies' in reply_data and reply_data['replies']:
                    reply_dict['replies'] = self._extract_replies(reply_data['replies'], reply_data['id'])

                processed_replies.append(reply_dict)

        return processed_replies   



    def _flatten_comments(self,comments):
        flattened = []
        for comment in comments:
            if 'body' in comment:  # Ensure there's a body key
                flattened.append(comment['body'])
            if 'replies' in comment and comment['replies']:  # Check if there are replies and it's not empty
                flattened.extend(self._flatten_comments(comment['replies']))  # Recursively process replies
        return flattened   
      
#if __name__=="__main__":
     

    #obj=DataExtraction()
    #print(obj.post_data_extract())

    #train_data,test_data=obj.initiate_data_ingestion()

    #data_transformation=DataTransformation()
    #train_arr,test_arr,_=data_transformation.initiate_data_transformation(train_data,test_data)

    #modeltrainer=ModelTrainer()
    #print(modeltrainer.initiate_model_trainer(train_arr, test_arr))
