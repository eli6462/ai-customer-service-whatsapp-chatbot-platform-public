from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient

from dotenv import load_dotenv
import os

# Load the environment variables from .env file
load_dotenv()

slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))

def test():

    response = slack_client.conversations_list()

    print('channels count:' + (str(len(response['channels']))))
    print()
    print(response)

test()