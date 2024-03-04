import os
import json
import sys
import torch
from transformers import pipeline, AutoTokenizer


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logging 
from exception import CustomException


class Transformer:

    def __init__(self):        

        self.summarizer_model = "sshleifer/distilbart-cnn-12-6"
        self.sentiment_model = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
        self.summarizer = pipeline("summarization", model=self.summarizer_model)
        self.analyzer = pipeline("sentiment-analysis", model=self.sentiment_model, revision="af0f99b")
        self.tokenizer_summarizer = AutoTokenizer.from_pretrained(self.summarizer_model)
        self.max_length=260
        self.min_length=30
        self.max_tokens = 512 


    def summarize_text(self, text):
        logging.info("Summarizing the data")
        try:
            # Check if text needs to be chunked based on token count
            tokenized_text = self.tokenizer_summarizer(text, truncation=True, return_tensors="pt")
            if tokenized_text.input_ids.size(1) > self.max_tokens:
                return self._summarize_long_text(text)
            else:
                summarized_text = self.summarizer(text, max_length=self.max_length, min_length=self.min_length, do_sample=False)
                return summarized_text[0].get('summary_text') if summarized_text else "Summarization not available for this text."
        except Exception as e:
            raise CustomException(e, sys)

    def _summarize_long_text(self, text):
        # Split the text into chunks that respect the token limit
        chunks = self._chunk_text(text, max_tokens=self.max_tokens)
        summarized_chunks = []
        for chunk in chunks:
            try:
                summarized_chunk = self.summarizer(chunk, max_length=self.max_length, min_length=self.min_length, do_sample=False)
                # Ensure that summarized_chunk is not empty before accessing its first element
                if summarized_chunk:
                    summary_text = summarized_chunk[0].get('summary_text', '')
                    if summary_text:  # Check if summary_text is not empty
                        summarized_chunks.append(summary_text)
            except Exception as e:
                logging.error(f"Error summarizing chunk: {e}")
                # Optionally append some default text or handle the error as needed
                summarized_chunks.append("Summarization not available for this chunk.")
        return ' '.join(summarized_chunks)

    def _chunk_text(self, text, max_tokens=500):
        # Naive implementation: split the text by periods to approximate sentence boundaries
        sentences = text.split('. ')
        chunks = []
        current_chunk = []

        for sentence in sentences:
            # Check if adding the next sentence would exceed the max_tokens limit
            if sum(len(s.split()) for s in current_chunk + [sentence]) > max_tokens:
                # If so, add the current chunk to the chunks list and start a new chunk
                chunks.append('. '.join(current_chunk))
                current_chunk = [sentence]
            else:
                # Otherwise, add the sentence to the current chunk
                current_chunk.append(sentence)

        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append('. '.join(current_chunk))

        return chunks
    
    def analyze_sentiment(self,text):
        logging.info("Analyzing the sentiment")
        try:
            # No need to tokenize here as 'pipeline' handles it, but be aware of the model's token limit
            result = self.analyzer(text[:self.max_tokens])  # Simple way to limit character count; consider tokenizing for accuracy
            return result
        except Exception as e:
            raise CustomException(e, sys)
    


if __name__=="__main__":
     
    data="Decided for the first time to try some cheap puts. I’ve been buying calls from Nov 1st to Jan (140-210) I missed the run from 210 to 238. When the ceo of panw said there clients are facing spending exhaustion I knew it was the case at a few other companies. Bought 5 minutes before close yesterday. I did not expect the figurde head who everyone loved to resign, got lucky there. I did buy some deep itm calls this morning as well. I think the new ceo will do good especially coming from Google. Sold both puts this morning."
    obj=Transformer()
    output = obj.sentiment_analyzer(data)

    print(output)
  

    