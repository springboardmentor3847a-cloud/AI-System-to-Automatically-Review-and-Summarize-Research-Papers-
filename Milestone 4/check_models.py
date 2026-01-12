import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- Checking Available Models ---")
try:
    for m in client.models.list():
        # Just print the name directly to see exactly what is allowed
        print(f"Found: {m.name}")
except Exception as e:
    print(f"Error: {e}")