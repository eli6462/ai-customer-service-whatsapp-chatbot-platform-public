from google.cloud import translate_v2 as translate

def list_languages():
    """Lists available translation languages."""

    client = translate.Client()
    languages = client.get_languages()

    for language in languages:
        print(f"{language['language']} - {language.get('name', 'Unknown')}")




def translate_text(text="YOUR_TEXT_HERE", project_id="ai-chatbot-translate-api"):
    """Translating Text."""

    client = translate.Client()

    result = client.translate(
        text, target_language='en',
    )

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))

# Example usage
#translate_text(text="זה עובד", project_id="your-project-id")

list_languages()
