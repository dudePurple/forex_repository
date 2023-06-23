import logging
import openai
import os
from settings import DEFAULT_ANSWER

openai.api_key = os.getenv('OPENAI_API_KEY')
messages = [
    {"role": "system",
     "content": "Answer the question."}
]


def get_answer(question: str):
    reply = DEFAULT_ANSWER
    if not openai.api_key:
        return reply

    try:
        messages.append({"role": "user", "content": question})
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        if (
                hasattr(chat, 'choices')
                and chat.choices
                and hasattr(chat.choices[0], 'message')
                and hasattr(chat.choices[0].message, 'content')
        ):
            reply = chat.choices[0].message.content

    except openai.error.OpenAIError as e:
        # Handle OpenAI API errors
        logging.info("OpenAI API error:", str(e))
    except Exception as e:
        # Handle other unexpected exceptions
        logging.info("An error occurred:", str(e))

    return reply
