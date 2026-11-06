
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=api_key)

MODEL = "gemini-3.8-flash"

print("Testing Gemini API...")
print("Model:", MODEL)

try:
    response = client.interactions.create(
        model=MODEL,
        input=(
            "Explain in two sentences why "
            "metagenomic abundance data are compositional."
        )
    )

    print("\n===== GEMINI RESPONSE =====")

    # Interactions API response
    print(response.output_text)

    print("\nGemini API test completed successfully.")

except Exception as e:
    print("\nGemini API request failed.")
    print("Error type:", type(e).__name__)
    print("Error:", str(e))
