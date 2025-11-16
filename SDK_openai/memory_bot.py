from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

messages = []  # will hold conversation history

print("Chat started (type 'exit' to quit)\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Chat ended.")
        break

    # add user input
    messages.append({"role": "user", "content": user_input})

    # send entire history
    response = client.responses.create(
        model="gpt-5-nano",
        input=messages
    )

    # extract and print assistant reply
    reply = response.output_text
    print("Assistant:", reply)

    # add assistant reply
    messages.append({"role": "assistant", "content": reply})
