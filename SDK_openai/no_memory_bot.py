from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

# Hardcoded API key (NOT recommended for production)
client = OpenAI()

print("Chat started (type 'exit' to quit)\n")

while True:
    # Take user input
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Chat ended.")
        break

    # Call responses API
    response = client.responses.create(
        model="gpt-5-nano",
        input=user_input
    )

    # Print model output
    print("Assistant:", response.output_text)
