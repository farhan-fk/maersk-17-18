# Simple Tool Combination Demo
# This shows how OpenAI can combine multiple tools to solve problems

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

print("🔧 Tool Combination Demo: Web Search + Code Interpreter")
print("=" * 60)

# Example 1: Simple calculation with web data
print("\n📊 Example 1: Current data + calculation")
response = client.responses.create(
    model="gpt-5-nano",
    tools=[
        {"type": "web_search"},
        {"type": "code_interpreter", "container": {"type": "auto"}}
    ],
    input="Find the current population of India and calculate how many people that is per square kilometer. India's area is 3.287 million km². Show your calculation step by step."
)

print("✅ Result:")
print(response.output_text)

print("\n" + "="*60)

# Example 2: Simple analysis
print("\n📈 Example 2: Research + analysis")
response2 = client.responses.create(
    model="gpt-5-nano",
    tools=[
        {"type": "web_search"},
        {"type": "code_interpreter", "container": {"type": "auto"}}
    ],
    input="Find Infosys's current stock price and calculate what a $1000 investment made 1 year ago would be worth today.Today is 16th Nov 2025,"
)

print("✅ Result:")
print(response2.output_text)

print("\n" + "="*60)
print("🎯 Key Learning: OpenAI automatically chose which tools to use and in what order!")
print("   • Web search for current data")
print("   • Code interpreter for calculations") 
print("   • All combined seamlessly!")