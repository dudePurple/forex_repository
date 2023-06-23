import openai
import os
from settings import DEFAULT_ANSWER

openai.api_key = os.getenv('OPENAI_API_KEY')
messages = [
    {"role": "system",
     "content": "You are a intelligent assistant."}
]


def get_answer(question: str):
    if not openai.api_key:
        reply = DEFAULT_ANSWER
    else:
        messages.append({"role": "user", "content": question})
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        reply = chat.choices[0].message.content

    return reply
