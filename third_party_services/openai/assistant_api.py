from threading import Thread

def get_run_status_with_timeout(client, thread_id, run_id, timeout):
    """
    Attempts to retrieve the run status with a timeout.
    Returns the run status if successful, None if timed out.
    """
    result = {'status': None, 'retrieved': False}

    def attempt_retrieve():
        try:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            result['status'] = run_status.status
            result['retrieved'] = True
        except Exception as e:
            print(f"Error retrieving run status: {e}")
            result['retrieved'] = False

    thread = Thread(target=attempt_retrieve)
    thread.start()
    thread.join(timeout=timeout)
    if thread.is_alive():
        print("Operation timed out")
    return result

def get_messages_with_timeout(client, thread_id, timeout):
    """
    Attempts to list messages with a timeout.
    Returns the messages if successful, None if timed out.
    """
    result = {'messages': None, 'retrieved': False}

    def attempt_list_messages():
        try:
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            result['messages'] = messages
            result['retrieved'] = True
        except Exception as e:
            print(f"Error listing messages: {e}")
            result['retrieved'] = False

    thread = Thread(target=attempt_list_messages)
    thread.start()
    thread.join(timeout=timeout)
    if thread.is_alive():
        print("Operation timed out")
    return result

def create_run_with_timeout(client, thread_id, assistant_id, timeout):
    """
    Attempts to create a run with a timeout.
    Returns the run if successful, None if timed out.
    """
    result = {'run': None, 'retrieved': False}

    def attempt_create_run():
        try:
            run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
            result['run'] = run
            result['retrieved'] = True
        except Exception as e:
            print(f"Error creating run: {e}")
            result['retrieved'] = False

    thread = Thread(target=attempt_create_run)
    thread.start()
    thread.join(timeout=timeout)
    if thread.is_alive():
        print("Operation timed out")
    return result

def create_thread_with_timeout(client, timeout):
    """
    Attempts to create a thread with a timeout.
    Returns the thread if successful, None if timed out.
    """
    result = {'thread': None, 'retrieved': False}

    def attempt_create_thread():
        try:
            thread = client.beta.threads.create()
            result['thread'] = thread
            result['retrieved'] = True
        except Exception as e:
            print(f"Error creating thread: {e}")
            result['retrieved'] = False

    thread = Thread(target=attempt_create_thread)
    thread.start()
    thread.join(timeout=timeout)
    if thread.is_alive():
        print("Operation timed out")
    return result