from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()
OpenAI.api_key  = os.getenv('OPENAI_API_KEY')

response = client.responses.create(
    model="gpt-5-nano",
    input="Tell me Maersk company inception story in 200 words max"

)

print(response.output_text)
