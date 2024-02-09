import sys
import os
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer 
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline 
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logging 
from exception import CustomException
from utils import save_object

@dataclass
class DataTransformationConfig: 
    preprocessor_obj_file_path=os.path.join('artifacts','preprocessor.pkl')

class DataTransformation:
    def __init__(self):
        self.data_transformation_config=DataTransformationConfig()
    
    def get_data_transformer_object(self):
        try:
            numerical_columns = ["writing_score", "reading_score"]
            categorical_columns = [
                "gender",
                "race_ethnicity",
                "parental_level_of_education",
                "lunch",
                "test_preparation_course",
            ]
            # numerical pipeline
            num_pipeline=Pipeline(
                steps=[
                ("imputer",SimpleImputer(strategy="median")),
                ("scaler",StandardScaler())

                ]
            )
            # 'imputer' is used to handle the missing value. The strategy="median" argument specifies that 
            # the imputer should replace missing values using the median of each column. 
            # Other possible values are: mean, most_frequent or some constant number
            # 'scaler' - scaling the num values.  the StandardScaler step is typically used after data cleaning and before feeding 
            # the data into a machine learning model. 
            # It ensures that the model is not unduly influenced by the scale of different features.

            cat_pipeline=Pipeline(
                steps=[
                ("imputer",SimpleImputer(strategy="most_frequent")),
                ("one_hot_encoder",OneHotEncoder()),
                ("scaler",StandardScaler(with_mean=False))
                ]
            )

  

            preprocessor=ColumnTransformer(
                [
                ("num_pipeline",num_pipeline,numerical_columns),
                ("cat_pipelines",cat_pipeline,categorical_columns)

                ]
            )
            # The main goal of the ColumnTransformer is to allow different transformations 
            # to be applied to different columns in the input data. 

            logging.info(f"Numerical columns {numerical_columns}")
            logging.info(f"Categorical columns {categorical_columns}")

            return preprocessor

        except Exception as e:
            raise CustomException(e,sys)
        

    def initiate_data_transformation(self,train_path, test_path):
        try:
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)

            logging.info("Read train and test data completed")

            logging.info("Obtaining preprocessing object")

            preprocessing_obj=self.get_data_transformer_object()
            #preprocessing_obj contains all the required parameters/pipeline to transform the data 

            target_column_name="math_score"
            numerical_columns = ["writing_score", "reading_score"]

            input_feature_train_df=train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df=train_df[target_column_name]

            input_feature_test_df=test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df=test_df[target_column_name]

            logging.info(
                f"Applying preprocessing object on training dataframe and testing dataframe."
            )

            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr=preprocessing_obj.transform(input_feature_test_df)
            # 'fit' calculates and stores the required parameters needed for training
            # 'transform' apply the transformation 
            # 'transform' is a method from ColumnTransformer 

            train_arr = np.c_[
                input_feature_train_arr, np.array(target_feature_train_df)
            ]
            test_arr = np.c_[
                input_feature_test_arr, np.array(target_feature_test_df)
            ]
            # combine the preprocessed input features with the target features (labels) for 
            # both the training and test datasets into single NumPy arrays, respectively. 
            # This is typically done to prepare the data for modeling, where you need both 
            # the input features and the target variable in a structured format
            # np.c_ is numpy concacatenation. 

            logging.info(f"Saved preprocessing object.")

            save_object(

                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessing_obj

            )

            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path,
            )
        except Exception as e:
            raise CustomException(e,sys)
