from google.cloud import translate_v2 as translate
import time

def list_languages():
    """Lists available translation languages."""

    client = translate.Client()
    languages = client.get_languages()

    for language in languages:
        print(f"{language['language']} - {language.get('name', 'Unknown')}")




def translate_text(text, target_language,client):
    """Translating Text."""

    # start measure translate time
    start_time = time.time()

    result = client.translate(
        text,
        target_language= target_language ,
        format_ = 'text'
    )
    # english - 'en'
    # hebrew - 'iw'

    # finish measure translate time
    end_time = time.time()
    duration = end_time - start_time


    print()
    print(f"Translation response time: {duration:.4f} seconds")
    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    print()

    return result["translatedText"]
