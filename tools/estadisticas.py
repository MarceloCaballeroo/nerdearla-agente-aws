import json
from pathlib import Path
from typing import Optional

BIBLIOTECA_PATH = Path(__file__).parent.parent / "data" / "anime_procesado.json"

_biblioteca = None


def get_biblioteca() -> list[dict]:
    global _biblioteca
    if _biblioteca is None:
        with open(BIBLIOTECA_PATH, encoding="utf-8") as f:
            _biblioteca = json.load(f)
    return _biblioteca


def analizar_estadisticas(genero: Optional[str] = None) -> str:
    biblioteca = get_biblioteca()

    if genero:
        biblioteca = [
            a
            for a in biblioteca
            if any(genero.lower() in tag.lower() for tag in a.get("tags", []))
        ]
        label = f" para género '{genero}'"
    else:
        label = " generales"

    if not biblioteca:
        return f"No hay animes{label} para analizar."

    ratings = [a["rating"] for a in biblioteca if a.get("rating") is not None]
    years = [a["release_year"] for a in biblioteca if a.get("release_year") is not None]

    estudios_count = {}
    for anime in biblioteca:
        for studio in anime.get("studios", []):
            estudios_count[studio] = estudios_count.get(studio, 0) + 1

    top_estudios = sorted(estudios_count.items(), key=lambda x: x[1], reverse=True)[:10]

    tipos_count = {}
    for anime in biblioteca:
        t = anime.get("type", "Unknown")
        tipos_count[t] = tipos_count.get(t, 0) + 1

    tags_count = {}
    for anime in biblioteca:
        for tag in anime.get("tags", []):
            tags_count[tag] = tags_count.get(tag, 0) + 1

    top_tags = sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:15]

    rating_promedio = sum(ratings) / len(ratings) if ratings else 0
    rating_max = max(ratings) if ratings else 0
    rating_min = min(ratings) if ratings else 0

    anio_promedio = sum(years) / len(years) if years else 0
    anio_min = min(years) if years else 0
    anio_max = max(years) if years else 0

    return json.dumps(
        {
            f"estadisticas{label}": {
                "total_animes": len(biblioteca),
                "rating": {
                    "promedio": round(rating_promedio, 2),
                    "maximo": rating_max,
                    "minimo": rating_min,
                },
                "anios": {
                    "promedio": round(anio_promedio, 1),
                    "rango": f"{anio_min} - {anio_max}",
                },
                "por_tipo": dict(
                    sorted(tipos_count.items(), key=lambda x: x[1], reverse=True)
                ),
                "top_10_estudios": dict(top_estudios),
                "top_15_tags": dict(top_tags),
            }
        },
        ensure_ascii=False,
        indent=2,
    )


def ranking_top(n: int = 20, genero: Optional[str] = None) -> str:
    biblioteca = get_biblioteca()

    if genero:
        biblioteca = [
            a
            for a in biblioteca
            if any(genero.lower() in tag.lower() for tag in a.get("tags", []))
        ]

    ranked = [a for a in biblioteca if a.get("rating") is not None]
    ranked.sort(key=lambda x: x["rating"], reverse=True)

    resultados = []
    for anime in ranked[:n]:
        resultados.append(
            {
                "rank": anime["rank"],
                "name": anime["name"],
                "rating": anime["rating"],
                "release_year": anime["release_year"],
                "studios": anime.get("studios", []),
                "tags": anime.get("tags", [])[:5],
            }
        )

    return json.dumps(resultados, ensure_ascii=False, indent=2)
