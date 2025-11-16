
from openai import OpenAI
import os
import base64
from dotenv import load_dotenv
load_dotenv()



client = OpenAI() 

response = client.responses.create(
    model="gpt-5-nano",
    input="Generate an image of Maersk Shipping anchoring at a beautiful isolated island in the Caribbean during sunset." \
         " The image should feature vibrant colors, clear waters, and a serene atmosphere.",
    tools=[{"type": "image_generation"}],
)

# Save the image to a file
image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]
    
if image_data:
    image_base64 = image_data[0]
    with open("maersk_mars.png", "wb") as f:
        f.write(base64.b64decode(image_base64))