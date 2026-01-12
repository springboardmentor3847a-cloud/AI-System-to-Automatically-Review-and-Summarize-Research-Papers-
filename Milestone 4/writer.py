import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

def generate_summary(text_content):
    prompt = f"""
    Analyze this research paper text. 
    Report: 1. Objective 2. Methods 3. Results 4. Limitations
    TEXT: {text_content[:30000]}
    """
    
    # EXACT NAMES from your available model list
    models_to_try = [
        "gemini-flash-latest",       # Try this first (Standard Free)
        "gemini-2.0-flash-exp",      # Try this second (Experimental Free)
        "gemini-1.5-flash-latest"    # Backup alias
    ]
    
    for model in models_to_try:
        try:
            print(f"   --> Asking AI ({model})...")
            response = client.models.generate_content(
                model=model, 
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "429" in str(e):
                print("   ⏳ Rate Limit. Waiting 5s...")
                time.sleep(5)
            elif "404" in str(e):
                print(f"   ⚠️ {model} not found. Trying next...")
                
    return "❌ Error: Could not generate summary. All models failed."