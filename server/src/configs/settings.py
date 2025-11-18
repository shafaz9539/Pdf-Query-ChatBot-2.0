import os
from dotenv import load_dotenv

load_dotenv()  # loads .env

GENAI_API_KEY = os.getenv("GENAI_API_KEY")

if GENAI_API_KEY is None:
    raise ValueError("GENAI_API_KEY not found. Add it to your .env file.")
