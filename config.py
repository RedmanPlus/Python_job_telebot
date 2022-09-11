import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT TOKEN')
CHANNELS_FOR_SUB =[os.getenv('PYTHON_JOB_STR_ID'), #Python 
                   os.getenv('REACT_JOB_STR_ID'), #React
                   os.getenv('JAVA_JOB_STR_ID') ]#Java
