from openai import OpenAI
import json

from dotenv import load_dotenv
import os

# Load the environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

assistant_file_path = '../assistant.json'

if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
        assistant_data = json.load(file)
        assistant_id = assistant_data['assistant_id']
        print("Loaded existing assistant ID.")

client = OpenAI(
    api_key=OPENAI_API_KEY)

assistant_files = client.beta.assistants.files.list(
  assistant_id = assistant_id
)
print(assistant_files)
