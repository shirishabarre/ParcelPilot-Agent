import os
import streamlit as st
from google import genai


def get_config(key, default=None):
    try:
        value = st.secrets.get(key)
        if value:
            return value
    except Exception:
        pass

    value = os.getenv(key)

    if value:
        return value

    return default


def get_gemini_api_key():
    api_key = get_config("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add GEMINI_API_KEY to Streamlit Secrets."
        )

    return api_key


class GeminiClient:

    def __init__(self):
        self.model = get_config(
            "GEMINI_MODEL",
            "gemini-2.0-flash",
        )

        self.client = genai.Client(
            api_key=get_gemini_api_key()
        )

    def generate(self, prompt):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text


def get_llm_client():
    provider = get_config(
        "LLM_PROVIDER",
        "gemini",
    ).lower()

    if provider != "gemini":
        raise RuntimeError(
            f"Unsupported LLM_PROVIDER: {provider}"
        )

    return GeminiClient()
