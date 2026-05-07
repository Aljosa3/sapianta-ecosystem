import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_llm(messages):
    """
    Send conversation messages to LLM and return response text.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2,
    )

    return response.choices[0].message.content
