import json
from pathlib import Path
from services.embedding import get_embedding
from services.chromadb import (
    search_similar,
    collection_exists,
    get_or_create_collection,
    add_animes_to_collection,
)
from services.embedding import get_embeddings_batch
from typing import Optional

BIBLIOTECA_PATH = Path(__file__).parent.parent / "data" / "anime_procesado.json"

_biblioteca = None


def get_biblioteca() -> list[dict]:
    global _biblioteca
    if _biblioteca is None:
        with open(BIBLIOTECA_PATH, encoding="utf-8") as f:
            _biblioteca = json.load(f)
    return _biblioteca


def indexar_animes():
    biblioteca = get_biblioteca()

    if collection_exists("anime_embeddings"):
        print("Colección ya existe, omitiendo indexado.")
        return

    print(f"Indexando {len(biblioteca)} animes...")
    texts = [
        f"{anime['name']}. {anime.get('description', '')} Tags: {', '.join(anime.get('tags', []))}"
        for anime in biblioteca
    ]

    batch_size = 100
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        embeddings = get_embeddings_batch(batch)
        all_embeddings.extend(embeddings)
        print(f"  Indexados {min(i + batch_size, len(texts))}/{len(texts)}")

    add_animes_to_collection(biblioteca, all_embeddings)
    print("Indexado completado!")


def recomendar_anime(descripcion: str, n_resultados: int = 10) -> str:
    if not collection_exists("anime_embeddings"):
        indexar_animes()

    query_embedding = get_embedding(descripcion)
    similares = search_similar(query_embedding, n_results=n_resultados)

    biblioteca = get_biblioteca()
    rank_to_anime = {a["rank"]: a for a in biblioteca}

    resultados = []
    for sim in similares:
        anime = rank_to_anime.get(sim["rank"])
        if anime:
            resultados.append(
                {
                    "rank": anime["rank"],
                    "name": anime["name"],
                    "rating": anime.get("rating"),
                    "release_year": anime.get("release_year"),
                    "studios": anime.get("studios", []),
                    "tags": anime.get("tags", [])[:10],
                    "description": anime.get("description", "")[:300],
                    "similarity_score": 1 - sim.get("distance", 0)
                    if sim.get("distance")
                    else None,
                }
            )

    if not resultados:
        return "No encontré recomendaciones basadas en tu descripción."

    return json.dumps(resultados, ensure_ascii=False, indent=2)


def recomendar_por_tags(
    tags: list[str], exclude_ranks: list[int] = None, n_resultados: int = 10
) -> str:
    biblioteca = get_biblioteca()

    if exclude_ranks is None:
        exclude_ranks = []

    scored = []
    for anime in biblioteca:
        if anime["rank"] in exclude_ranks:
            continue
        anime_tags = [t.lower() for t in anime.get("tags", [])]
        match_count = sum(
            1 for tag in tags if any(tag.lower() in mt for mt in anime_tags)
        )
        if match_count > 0:
            score = match_count / len(tags)
            if anime.get("rating"):
                score += anime["rating"] / 10
            scored.append((score, anime))

    scored.sort(key=lambda x: x[0], reverse=True)
    resultados = []
    for score, anime in scored[:n_resultados]:
        resultados.append(
            {
                "rank": anime["rank"],
                "name": anime["name"],
                "rating": anime.get("rating"),
                "release_year": anime.get("release_year"),
                "studios": anime.get("studios", []),
                "tags": anime.get("tags", [])[:10],
                "match_score": round(score, 3),
            }
        )

    if not resultados:
        return "No encontré recomendaciones con esas etiquetas."

    return json.dumps(resultados, ensure_ascii=False, indent=2)
