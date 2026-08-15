import os

from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()


def get_llm():
    api_key = os.getenv("NVIDIA_API_KEY")
    model = os.getenv("NVIDIA_MODEL")

    if not api_key:
        raise ValueError("NVIDIA_API_KEY is not set.")

    if not model:
        raise ValueError("NVIDIA_MODEL is not set.")

    return ChatNVIDIA(
        model=model,
        temperature=0,
        max_tokens=2048,
    )