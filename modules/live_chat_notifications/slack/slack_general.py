from slack_sdk.errors import SlackApiError

# *******************************
# Slack Channels
# *******************************

def create_slack_channel_in_background(slack_client,thread_id,user_ids):
    try:
        # encode the thread ID to a format that is acceptable as a Slack conversation name
        # (slack conversation names cannot contain uppercase letters)
        encoded_thread_id = encode_thread_id_to_slack(thread_id)

        # Replace 'thread_name' with your desired channel name logic
        result = slack_client.conversations_create(
            name=encoded_thread_id,
            is_private=True  # Set to True if you want a private channel
        )
        channel_id = result["channel"]["id"]
        print(f"Slack Channel created: {channel_id} for thread_id: {thread_id}")

        # invite relevant users to channel
        invite_users_to_channel(slack_client, channel_id, user_ids)

    except SlackApiError as e:
        print(f"Error creating Slack channel for thread_id: {thread_id}: {e.response['error']}")


def invite_users_to_channel(slack_client, channel_id, user_ids):
    try:
        for user_id in user_ids:
            slack_client.conversations_invite(channel=channel_id, users=[user_id])
            print(f"Invited user {user_id} to channel {channel_id}")
    except SlackApiError as e:
        print(f"Error inviting users to Slack channel: {e.response['error']}")


def encode_thread_id_to_slack(thread_id):
    # Ensure the thread ID format is as expected
    if not thread_id.startswith("thread_"):
        raise ValueError("Invalid thread ID format")

    # Extract the part after "thread_"
    unique_part = thread_id[7:]

    # Replace uppercase letters with '-lowercase'
    encoded = ''.join(f"-{char.lower()}" if char.isupper() else char for char in unique_part)

    # Prepend "thread_" back to the encoded unique part
    encoded_thread_id = "thread_" + encoded

    return encoded_thread_id


# *******************************
# Slack chat messages
# *******************************

# find_slack_channel_id(): for now, I don't use this function.
# and changed the way of passing the 'channel' parameter to the slack_client.chat_postMessage() method.
# I now pass the name of the channel and not it's id.
# the API method: slack_client.conversations_list() uses pagination, and has a limit of 1000 conversation per page.
# to avoid developing a method for fetching all pages, and minimize processing times for sending a Slack message,
# I switched to passing the channel name to the 'channel' parameter in 'slack_client.chat_postMessage',
# instead of searching for the channel ID, in what may be in the future. lots of pages each containing 1000 conversations.

def find_slack_channel_id(slack_client, encoded_thread_id):
    try:
        response = slack_client.conversations_list()
        for channel in response['channels']:
            if channel['name'] == encoded_thread_id:
                return channel['id']
    except SlackApiError as e:
        print(f"Error finding Slack channel: {e.response['error']}")
    return None

def post_message_to_slack(slack_client, channel_name, user_message, chatbot_response):
    try:
        formatted_message = f"\n\nUser's message:\n\n{user_message}\n\n\n###**********###\nAI chatbot answer:\n###**********###\n\n{chatbot_response}"
        slack_client.chat_postMessage(channel=channel_name, text=formatted_message)
        print('Message posted to Slack.')
    except SlackApiError as e:
        print(f"Error posting message to Slack: {e.response['error']}")

def post_to_slack_background(slack_client, thread_id, user_message, chatbot_response):
    encoded_thread_id = encode_thread_id_to_slack(thread_id)

    # for now I will pass the channel_name and not the channel ID,
    # to reduce the complication of developing a method that will fetch all conversation 'pages' in a serial manner, one by one.
    # more details about the decision in the comments on the 'find_slack_channel_id()' function.
    '''
    channel_id = find_slack_channel_id(slack_client, encoded_thread_id)
    if channel_id:
        post_message_to_slack(slack_client, channel_id, user_message, chatbot_response)
    else:
        print("Slack channel not found, can't post message.")
    '''
    if encoded_thread_id:
        post_message_to_slack(slack_client, encoded_thread_id, user_message, chatbot_response)
    else:
        print("Can't post Slack Message: Error in encoding the assistant API thread ID into a Slack channel name.")
