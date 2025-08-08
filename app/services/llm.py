import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()
MODEL = "gemini-2.0-flash-lite-001"
