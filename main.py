import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import openai
from werkzeug.serving import run_simple
from threading import Thread

from slack_sdk.errors import SlackApiError

from dotenv import load_dotenv
import os

# my scripts
from third_party_services.google.translate_API.translate import translate_text
from third_party_services.openai.assistant_api import *
from modules.security.input_sanitization.input_sanitization import *
from modules.live_chat_notifications.slack.slack_general import *
from configs import *
from flask_migrate import Migrate
# Load the environment variables from .env file
load_dotenv()

from models import *

###############################################
# import routes
###############################################

# import routes
from routes.whatsapp.whatsapp_route import whatsapp_bp

# Register blueprints
app.register_blueprint(whatsapp_bp)


##########################################################################################################
# important: the main (and currently only) route in this app is 'whatsapp_route.py'
# in './routes/whatsapp/whatsapp_route.py'.
# this route is used to communicate with customers/users using whatsapp business chat.
#
# information that is less important for someone who wants to do a quick review of this repository:
# (just as background for those who are interested)
#
# there were previously 2 other routes,
# directly in main.py - used as a backend for a 'live website chat' version of this AI chatbot,
# (and using webflow's pre-built front-end for website chat interfaces).
# those 2 routes were removed in the 'exposed public version' of this repository,
# since they lag behind in updates and features for at least few development month,
# they were used as the pre-mvp version,
# just to be able to easily and quickly test the user experience of such an AI customer service chatbot.
# now I concentrate mostly on the whatsapp business chat interface, and want to emphasize its significance in this app.
#######################################################################################################################

# Run server
if __name__ == '__main__':
    run_simple('0.0.0.0', 8080, app, threaded=True)
