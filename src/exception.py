import sys 
import logging

def error_message_detail(error, error_detail:sys):
    _,_,exc_tb=error_detail.exc_info()

    # sys.exc_info() returns a tuple of three values: (type, value, traceback).
    # type is the exception type.
    # value is the exception instance.
    # traceback is a traceback object which encapsulates the call stack at the point where the exception originally occurred.


    file_name=exc_tb.tb_frame.f_code.co_filename
    # tb_frame is an attribute of the traceback object (exc_tb), 
    # which refers to the execution frame at the current level of the traceback.

    error_message="Error occurred in Python script name [{0}] line name [{1}] error message [{2}]".format(
        file_name, exc_tb.tb_lineno, str(error)
    )
    return error_message


class CustomException(Exception):
    def __init__(self, error_message, error_detail:sys):
        super().__init__(error_message)
        self.error_message=error_message_detail(error_message, error_detail=error_detail)

    def __str__(self):
        return self.error_message
    

# example of the usage
# Need to import: from logger import *
'''
if __name__=="__main__":
    try:
        a=1/0
    except Exception as e :
        logging.info("Error")
        print(logging.LOG_FILE_PATH)
        raise CustomException(e, sys) 
'''