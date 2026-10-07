from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key not found")
    exit()

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Generate one technical interview question for a Python developer fresher."
)

print("AI Interviewer")
print("--------------------")
print(response.text)