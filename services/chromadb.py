import chromadb
from chromadb.config import Settings
from pathlib import Path
import json

CHROMA_DB_PATH = Path(__file__).parent.parent / "chroma_data"

_client = None
_collection = None


def get_chroma_client():
    global _client
    if _client is None:
        CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
        _client = chromadb.Client(
            Settings(persist_directory=str(CHROMA_DB_PATH), anonymized_telemetry=False)
        )
    return _client


def get_or_create_collection(name: str = "anime_embeddings"):
    client = get_chroma_client()
    return client.get_or_create_collection(name=name)


def add_animes_to_collection(animes: list[dict], embeddings: list[list[float]]):
    collection = get_or_create_collection("anime_embeddings")

    ids = [str(anime["rank"]) for anime in animes]
    documents = [
        f"{anime['name']}. {anime.get('description', '')} Tags: {', '.join(anime.get('tags', []))}"
        for anime in animes
    ]
    metadatas = [
        {
            "name": anime["name"],
            "rank": anime["rank"],
            "rating": anime.get("rating"),
            "release_year": anime.get("release_year"),
            "studios": ", ".join(anime.get("studios", [])),
            "tags": ", ".join(anime.get("tags", []))[:500],
        }
        for anime in animes
    ]

    collection.add(
        ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
    )


def search_similar(query_embedding: list[float], n_results: int = 10) -> list[dict]:
    collection = get_or_create_collection("anime_embeddings")

    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)

    if not results["ids"] or not results["ids"][0]:
        return []

    similarities = []
    for i, idx in enumerate(results["ids"][0]):
        similarities.append(
            {
                "rank": int(idx),
                "name": results["metadatas"][0][i].get("name", ""),
                "rating": results["metadatas"][0][i].get("rating"),
                "release_year": results["metadatas"][0][i].get("release_year"),
                "studios": results["metadatas"][0][i].get("studios", ""),
                "tags": results["metadatas"][0][i].get("tags", ""),
                "distance": results["distances"][0][i]
                if "distances" in results
                else None,
            }
        )

    return similarities


def collection_exists(name: str = "anime_embeddings") -> bool:
    client = get_chroma_client()
    try:
        client.get_collection(name)
        return True
    except Exception:
        return False
