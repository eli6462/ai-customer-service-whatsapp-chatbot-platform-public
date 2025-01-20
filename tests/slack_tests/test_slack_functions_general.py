from dotenv import load_dotenv
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def test():
    # Load the environment variables from .env file
    load_dotenv()

    # Your Slack bot token
    slack_token = os.environ["SLACK_BOT_TOKEN"]
    client = WebClient(token=slack_token)

    # The user ID of the person you want to send a DM to
    user_id = ''  # there was some real user id here (previously),
    # it was removed as a security measure, before exposing this repository as public

    try:
        # Start a conversation with the user
        response = client.conversations_open(users=[user_id])
        channel_id = response["channel"]["id"]

        # Post a message to the conversation
        client.chat_postMessage(channel=channel_id, text="Hello! This is a test DM from the bot.")
        print("Message sent successfully.")
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        print(e.response["error"])
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
