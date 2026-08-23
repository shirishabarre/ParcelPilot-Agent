import os
import streamlit as st
from google import genai


def get_gemini_api_key():
    api_key = None

    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add GEMINI_API_KEY to Streamlit Secrets."
        )

    return api_key


class GeminiClient:

    def __init__(self):
        self.client = genai.Client(
            api_key=get_gemini_api_key()
        )

    def generate(self, prompt):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text


def get_llm_client():
    return GeminiClient()
