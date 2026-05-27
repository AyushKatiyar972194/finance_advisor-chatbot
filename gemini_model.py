from crewai import LLM
import os
from dotenv import load_dotenv

load_dotenv()

def get_gemini_model():
    return LLM(
        model="gemini/gemini-flash-lite-latest",
        api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.7
    )