import re
import bleach

# Regular expression for validating thread_id format
thread_id_pattern = re.compile(r'^thread_[a-zA-Z0-9]{24}$')

def validate_thread_id(thread_id):
    if not thread_id or not isinstance(thread_id, str):
        return False
    return bool(thread_id_pattern.match(thread_id))

def validate_message_length(message, max_length=1000):  # Example max_length
    return isinstance(message, str) and len(message) <= max_length

def sanitize_input(text):
    # Allow only safe HTML tags and attributes
    # bleach.clean removes unsafe tags/attributes
    return bleach.clean(text, strip=True)



