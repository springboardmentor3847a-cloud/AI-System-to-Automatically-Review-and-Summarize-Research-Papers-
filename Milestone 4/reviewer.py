import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def review_draft(draft):
    prompt = f"""
    Peer review the following research summary. 
    Identify 2 strengths and 1 potential area of improvement.
    
    SUMMARY: {draft}
    """
    
    # EXACT NAMES from your available model list
    models_to_try = [
        "gemini-flash-latest",       
        "gemini-2.0-flash-exp",      
        "gemini-1.5-flash-latest"    
    ]

    # --- THE FIX: Wait 15 seconds before starting to let the API cool down ---
    print("   ⏳ Waiting 15s for API cooldown before Peer Review...")
    time.sleep(15) 

    for model in models_to_try:
        try:
            print(f"   --> Reviewing with {model}...")
            response = client.models.generate_content(
                model=model, 
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "429" in str(e):
                print(f"   ⏳ Rate Limit on {model}. Waiting 10s...")
                time.sleep(10) # Wait even longer if it fails
                continue
    
    return "Review skipped due to high traffic."