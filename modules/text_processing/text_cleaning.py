import re

def clean_output(text):
    # Remove 【digit:digit†source】 patterns
    cleaned_text = re.sub(r"【\d+:\d+†source】", '', text)

    # Remove unnecessary line breaks and multiple spaces
    cleaned_text = re.sub(r"\n\s*\n", '\n', cleaned_text)  # Reduces multiple newlines to a single one

    # Trim unwanted spaces at the beginning and end of the text
    cleaned_text = cleaned_text.strip()

    # Remove periods at the end of the text if they are unwanted
    if cleaned_text.endswith("."):
        cleaned_text = cleaned_text[:-1]

    cleaned_text = cleaned_text.rstrip('\n')

    return cleaned_text


