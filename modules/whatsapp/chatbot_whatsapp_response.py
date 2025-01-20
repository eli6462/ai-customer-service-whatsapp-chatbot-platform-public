from twilio.rest import Client

from dotenv import load_dotenv
import os
from models import Business,BusinessCredentials

from sqlalchemy.orm import joinedload

# Load the environment variables from .env file
load_dotenv()

# load twilio secrets

def send_whatsapp_response(sender, response_message,business):

    client = None
    business_name = ""

    try:
        business_number = f"whatsapp:{business.business_whatsapp_number}"
        business_name = business.business_name
        client = Client(business.credentials.twilio_sid, business.credentials.twilio_auth_token)

        try:
            message = client.messages.create(
                body=response_message,
                from_=business_number,
                to=sender
            )
            print(f"Sent WhatsApp message to {sender},  from: {business_name}: {response_message}")
        except Exception as e:
            print(f'Error in sending WhatsApp message to {sender}, from: {business_name} Error: {e}')

    except Exception as e:
        print(f"Error in send_whatsapp_response to {sender}, from: {business_name}: {str(e)}")


