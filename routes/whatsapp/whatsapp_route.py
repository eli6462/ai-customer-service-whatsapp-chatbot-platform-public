from flask import Flask, request, jsonify, Blueprint
from modules.whatsapp.chatbot_whatsapp_response import *
import redis
import traceback
import requests
from concurrent.futures import ThreadPoolExecutor
from models import *
# Import the db_pool from config.py
from configs import *
from configs import client as openai_client
from sqlalchemy.orm import joinedload
from slack_sdk import WebClient

from modules.security.input_sanitization.input_sanitization import *
from modules.live_chat_notifications.slack.slack_general import *
from third_party_services.openai.assistant_api import *
from third_party_services.google.translate_API.translate import translate_text
from modules.text_processing.text_cleaning import *


def insert_thread_mapping(business,sender, thread_id):
    with app.app_context():
        try:
            sender_number = str(sender).split(':')[1]  # Extract the actual number
            user_client = Client.query.filter_by(whatsapp_number=sender_number).first()

            if user_client:
                client_id = user_client.id
            else:
                user_client = Client(whatsapp_number=sender_number)
                db.session.add(user_client)
                db.session.commit()
                print(f'New client created with id {user_client.id} and number {sender_number}, '
                      f'talked with business {business.business_name}, thread id: {thread_id}')
                client_id = user_client.id

            business_client = BusinessClient(business_id=business.id, client_id=client_id, ai_thread=thread_id)
            db.session.add(business_client)
            db.session.commit()
            print(f'Business-client junction table created successfully with id {business_client.id}, '
                  f'business name : {business.business_name}, client_number {sender_number} ,thread_id {thread_id} ')
        except Exception as e:
            print(f"Error inserting thread mapping for business {business.business_name}, thread id: {thread_id}, "
                  f"for sender {sender_number}: {e}")

    # No need for finally block to close db_conn or db_cursor here,
    # this is handled by the 'with get_db_connection() as db_conn:' block


def create_openai_user_message_recursive_retry(sender,business, thread_id, message_body, attempt=0 ):

    max_attempts = 6
    retry_time_seconds = 10

    try:
        # Attempt to add the user's message to the thread
        openai_client.beta.threads.messages.create(thread_id=thread_id, role="user", content=message_body)
        print(f'Added message to OpenAI successfully for sender: {sender}, for business: {business.business_name}, '
              f'thread_id: {thread_id}, message: {message_body}')

    except openai.BadRequestError as e:
        if attempt < max_attempts:

            print(f"BadRequestError caught: {e}. Retrying again after: {retry_time_seconds} seconds. "
                  f"Attempt: {attempt + 1}")
            sleep(retry_time_seconds)
            create_openai_user_message_recursive_retry(sender,business, thread_id, message_body, attempt + 1)
        else:
            print(f"Failed to add message after {max_attempts} attempts. Giving up. for sender: {sender}, "
                  f"for business: {business.business_name}, thread_id: {thread_id}, message: {message_body}")


# Initialize Redis connection
# Adjust host and port if your Redis setup differs
redis_conn = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=0, decode_responses=True)


# Create a Blueprint
whatsapp_bp = Blueprint('whatsapp', __name__)

@whatsapp_bp.route('/whatsapp', methods=['POST'])
def receive_whatsapp_message():
    try:

        # for tests
        # print('***********************',request.form)

        # get request data
        # message_sid = sanitize_input(request.form.get('MessageSid'))
        sender = sanitize_input(request.form.get('From'))
        receiver = sanitize_input(request.form.get('To'))
        message_body = sanitize_input(request.form.get('Body'))

        #receiver = receiver.split('+')[1]
        receiver = receiver.split(':')[1]

        ###############################################
        # fetch business details from DB
        ###############################################

        # query for the business DB record, and assistant and credentials tables records
        business = Business.query.options(
            joinedload(Business.ai_assistant),
            joinedload(Business.credentials),
            joinedload(Business.slack_user_ids)
        ).filter_by(business_whatsapp_number=receiver).first()

        print(f"Received WhatsApp message from {sender}, for business: {business.business_name if business else ''}, "
              f"message: {message_body}")

        # if business is not found, return a 500 internal server error
        # also if business is disabled, return a 403 requested resource is forbidden error
        if business and business.ai_assistant:
            assistant = business.ai_assistant
            if business.is_disabled:
                print(f'business: {business.business_name} received a message but is disabled, returning a 403 error.')
                return jsonify({"error": "This business is currently disabled."}), 403
        else:
            print(f'did not found a business or assistant in the DB associated with '
                  f'this receiver phone number: {receiver}, for sender: {sender}, returning a 500 error code.')
            return jsonify({"error": "Internal Server Error"}), 500

        # validate message
        if not validate_message_length(message_body):
            print(f'message-sending attempt has failed from {sender}: to business: {business.business_name} '
                  f'business whatsapp number: {business.business_whatsapp_number}, message too long.')
            return jsonify({"error": "Message is too long"}), 400

        # init slack client
        slack_client = WebClient(token=business.credentials.slack_bot_token)

        ###############################################
        # thread ID handling
        ###############################################

        # Attempt to retrieve the thread ID from Redis using the sender's WhatsApp number
        thread_id = None
        data = redis_conn.hgetall(f'{sender}_{receiver}')
        if data:
            thread_id = data.get('thread_id')

        db_result = None

        if thread_id is None:
            # ************************************
            # fetch business-client record from DB
            # ************************************

            print(
                f'\nDid NOT get cache hit for sender: {sender}, to business: {business.business_name} '
                f' thread_id: {thread_id},message that did NOT got cache hit:\n{message_body}\n')

            # Check the DB for the sender's number
            # be careful of confusing between production DB table names and development DB table names.
            try:
                sender_number = str(sender).split(':')[1]
                with app.app_context():
                    business_client = (BusinessClient.query.join(Client).join(Business).filter(Client.whatsapp_number == sender_number).filter(Business.business_whatsapp_number == receiver).first())
                    if business_client:
                        db_result = business_client
                        
            except Exception as e:
                print(
                    f'Error fetching from DB, for {thread_id} for sender: {sender}, '
                    f'to business: {business.business_name} for message {message_body}, error is: {e}')
            # No need for finally block to close db_conn or db_cursor here, this is handled by the 'with get_db_connection() as db_conn:' block

            if db_result:
                # ************************************
                # add DB result to cache
                # ************************************
                thread_id = db_result.ai_thread
                print(
                    f'\nDB hit for sender: {sender}, to business: {business.business_name}, '
                    f'thread_id: {thread_id}\nmessage that got DB hit:\n{message_body}\n')

                redis_conn.hmset(f'{sender}_{receiver}', {'from': sender,'to': receiver,'thread_id': thread_id})
            else:
                # *********************************
                # create a new thread
                # *********************************
                print(
                    f'\nDid NOT get DB hit for sender: {sender}, to business: {business.business_name} '
                    f', thread_id: {thread_id}\nmessage that did NOT get DB hit:\n{message_body}\n')

                thread_creation_attempt_count = 0
                MAX_THREAD_CREATION_ATTEMPTS = 10
                thread = None

                while True and thread_creation_attempt_count <= MAX_THREAD_CREATION_ATTEMPTS:

                    result = create_thread_with_timeout(openai_client, 3)

                    if result['retrieved']:
                        thread = result['thread']
                        thread_id = thread.id
                        break
                    else:
                        # Handle timeout or error
                        print(
                            f"Failed to create a thread or operation timed out, "
                            f"trying again for the number {thread_creation_attempt_count + 1} time.")

                    thread_creation_attempt_count += 1

                # end while

                if not thread:
                    print(
                        'failed to create a thread with openAI API after multiple retries, '
                        'returning a 500 internal server error code to client\n')
                    return jsonify({"error": "Internal Server Error"}), 500


                # *********************************
                # Slack - Create channel
                # *********************************
                slack_user_ids = [user.slack_user_id for user in business.slack_user_ids]

                # Create Slack channel in the background
                Thread(target=create_slack_channel_in_background, args=(slack_client, thread_id, slack_user_ids)).start()

                # *********************************
                # add thread ID to DB and cache it (in the background)
                # *********************************

                # Add to DB
                with ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(insert_thread_mapping,business, sender, thread_id)

                # Cache the new thread ID with the sender's number as the key
                # redis_conn.set(sender, thread_id)
                redis_conn.hmset(f'{sender}_{receiver}', {'from':sender,'to':receiver,'thread_id':thread_id})
        else:
            print(f'\nCache hit for sender: {sender}, to business: {business.business_name} '
                  f', thread_id: {thread_id}\nmessage that got cache hit:\n{message_body}\n')



        ###############################################
        # assistant API message creation handling
        ###############################################

        # translate user input to english with google translate API
        #user_input_english = translate_text(message_body, 'en', translate_client)

        # don't translate to english, keep hebrew or original language.
        user_input_english = message_body

        # Add the user's message to the thread, with recursive retry
        create_openai_user_message_recursive_retry(sender,business, thread_id, user_input_english, attempt=0 )

        # *********************************
        # create a run of the thread
        # *********************************

        run_attempt_count = 0
        MAX_RUN_ATTEMPTS = 10

        # to avoid errors of referencing run before it was initialized
        run = None

        assistant_id = assistant.ai_assistant_id

        while True and run_attempt_count <= MAX_RUN_ATTEMPTS:

            result = create_run_with_timeout(openai_client, thread_id, assistant_id, 3)

            if result['retrieved']:
                run = result['run']
                break
            else:
                # Handle timeout or error
                print(
                    f"Failed to create a run or operation timed out, trying again for the number {run_attempt_count + 1} time.")

            run_attempt_count += 1

        # end while

        if not run:
            print(
                f'failed to create a run with openAI API after multiple retries, '
                f'returning a 500 internal server error code to client, for business: {business.business_name}'
                f' client: {sender}, thread id: {thread_id}')
            return jsonify({"error": "Internal Server Error"}), 500

        # ***************************************************
        # Check if the Run requires action (function call)
        # ***************************************************

        while True:
            # run_status = client.beta.threads.runs.retrieve(
            run_status = get_run_status_with_timeout(openai_client, thread_id, run.id, 4)
            print(f"Run status for whatsapp thread ID - {thread_id}: {run_status['status']}")  # {run_status.status}
            if run_status['status'] == 'completed' or run_status['status'] == 'failed':  # run_status.status
                break
            sleep(1)  # Wait for a second before checking again

        # **********************************************************
        # Retrieve and return the latest message from the assistant
        # **********************************************************

        message_retrival_count = 0 
        MAX_MESSAGE_RETRIVAL_ATTEMPTS = 10

        # to avoid errors of referencing 'messages' before it was initialized
        messages = None

        while True and message_retrival_count <= MAX_MESSAGE_RETRIVAL_ATTEMPTS:

            result = get_messages_with_timeout(openai_client, thread_id, timeout=3)

            if result['retrieved']:
                messages = result['messages']
                break
            else:
                # Handle timeout or error
                print(
                    f"Failed to retrieve messages or operation timed out, trying again for the number {message_retrival_count + 1} time.")

            message_retrival_count += 1

        # end while

        if messages:
            response = messages.data[0].content[0].text.value
        else:
            print(
                f'failed to retrieve messages from openAI API after multiple retries, '
                f'returning a 500 internal server error code to client, '
                f'for business: {business.business_name}, client: {sender}, thread id: {thread_id}')
            return jsonify({"error": "Internal Server Error"}), 500

        # **********************************************************
        # translate GPT answer to Hebrew
        # **********************************************************

        # I disabled it for now, tested the assistants for a few weeks,
        # and it seems they follow the language instructions pretty strictly,
        # so there might be no need for the additional layer of the Google Translate API.
        #gpt_answer = translate_text(response, os.getenv('TARGET_LANGUAGE'), translate_client)

        gpt_answer_clean = clean_output(response)

        print(f"Assistant response for whatsapp thread ID - {thread_id}: {response}")  # Debugging line
        #print(f"Assistant response translated for whatsapp thread ID - {thread_id}: {gpt_answer}")
        print(f"Assistant response *cleaned* for whatsapp thread ID - {thread_id}: {gpt_answer_clean}")

        # send the response back to the user
        send_whatsapp_response(sender, gpt_answer_clean,business)

        # *********************************
        # Slack - Post message to channel
        # *********************************

        message_body_plus_senders_num = sender + '\n' + message_body
        
        # After generating the chatbot response and before returning the response in english:
        Thread(target=post_to_slack_background,
               args=(slack_client, thread_id, message_body_plus_senders_num , gpt_answer_clean))\
            .start()

        return jsonify(success=True), 200

    except Exception as e:
        # Prints the type of exception, the exception message, and the traceback
        print(f"Error in /whatsapp route: {type(e).__name__}: {str(e)}")
        traceback.print_exc()

        # Return a generic error message
        return jsonify(error="An error occurred"), 500
