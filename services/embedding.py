import os
import requests
from dotenv import load_dotenv

load_dotenv()

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.io/v1"


def get_embedding(text: str, model: str = "embo01") -> list[float]:
    if not MINIMAX_API_KEY:
        raise ValueError("MINIMAX_API_KEY no está configurada")

    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {"model": model, "input": text}

    response = requests.post(
        f"{MINIMAX_BASE_URL}/embeddings", headers=headers, json=payload, timeout=60
    )

    if response.status_code != 200:
        raise Exception(
            f"Embedding API error: {response.status_code} - {response.text}"
        )

    data = response.json()
    return data["data"][0]["embedding"]


def get_embeddings_batch(texts: list[str], model: str = "embo01") -> list[list[float]]:
    if not MINIMAX_API_KEY:
        raise ValueError("MINIMAX_API_KEY no está configurada")

    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {"model": model, "input": texts}

    response = requests.post(
        f"{MINIMAX_BASE_URL}/embeddings", headers=headers, json=payload, timeout=120
    )

    if response.status_code != 200:
        raise Exception(
            f"Embedding API error: {response.status_code} - {response.text}"
        )

    data = response.json()
    return [item["embedding"] for item in data["data"]]
