import mysql.connector.pooling

import openai
from openai import OpenAI
from packaging import version

# old version 2 google translate (probably the 'machine' translate model, not the 'ai' translate model)
from google.cloud import translate_v2 as translate

from time import sleep
import functions

from dotenv import load_dotenv
import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Load the environment variables from .env file
load_dotenv()

##########################################################
# RDS production Database
##########################################################

# Load DB config from environment variables
db_config = {
    "host": os.getenv('DB_HOST'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "database": os.getenv('DATABASE')
}

'''
# Initialize MySQL connection pool
db_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="my_pool",
                                                      pool_size=15,  # Adjust as necessary
                                                      **db_config)
'''

##########################################################
# Flask app and DB
##########################################################



DB_HOST = db_config['host']
DB_USER = db_config['user']
DB_PASSWORD = db_config['password']
DATABASE = db_config['database']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DATABASE}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


##########################################################
# OpenAI
##########################################################

# Check OpenAI version is correct
required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if current_version < required_version:
  raise ValueError(f"Error: OpenAI version {openai.__version__}"
                   " is less than the required version 1.1.1")
else:
  print("OpenAI version is compatible.")

# Init client
client = OpenAI(
    api_key=OPENAI_API_KEY)  # should use env variable OPENAI_API_KEY in secrets (bottom left corner)

##########################################################
# Google Translate
##########################################################

# init google translate client
'''
def get_credentials():
  """
  Fetches Google API client credentials, prioritizing environment variable first.

  Returns:
      google.oauth2.service_account.Credentials: The loaded credentials object.
  """

  # Check for environment variable first
  if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    # Use credentials from environment variable if present
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
  else:
    # Fallback to credentials file path from .env (if available)
    credentials_path = 'G:/Flask/AI_chatbot_escape_rooms_api-whatsapp-api-integration/env_files/ai-chatbot-translate-api-886891de2fce.json'

  # Load credentials
  credentials = service_account.Credentials.from_service_account_file(credentials_path)
  return credentials
'''

# old version 2 google translate (probably the 'machine' translate model, not the 'ai' translate model)
#translate_client = translate.Client(credentials=get_credentials())
translate_client = translate.Client()

##########################################################
# Slack
##########################################################

# load slack user IDs
# (these user ids are now fetched from the DB)

#slack_user_ids_str = os.getenv('SLACK_USER_IDS_LIST', '')
#slack_user_ids_list = slack_user_ids_str.split(',')

# create a slack web client
# (this client will now be created dynamically according to a slack bot token fetched from the DB)
#slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))