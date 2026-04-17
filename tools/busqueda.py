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


def guardar_biblioteca(biblioteca: list[dict]):
    with open(BIBLIOTECA_PATH, "w", encoding="utf-8") as f:
        json.dump(biblioteca, f, ensure_ascii=False, indent=2)
    global _biblioteca
    _biblioteca = None


def buscar_anime(
    genero: str = "",
    estudio: str = "",
    tipo: str = "",
    anio_min: Optional[int] = None,
    anio_max: Optional[int] = None,
    rating_min: Optional[float] = None,
    nombre: str = "",
) -> str:
    biblioteca = get_biblioteca()
    resultados = biblioteca

    if nombre:
        resultados = [a for a in resultados if nombre.lower() in a["name"].lower()]

    if genero:
        resultados = [
            a
            for a in resultados
            if any(genero.lower() in tag.lower() for tag in a.get("tags", []))
        ]

    if estudio:
        resultados = [
            a
            for a in resultados
            if any(estudio.lower() in studio.lower() for studio in a.get("studios", []))
        ]

    if tipo:
        resultados = [
            a for a in resultados if tipo.lower() in a.get("type", "").lower()
        ]

    if anio_min is not None:
        resultados = [
            a
            for a in resultados
            if a.get("release_year") is not None and a["release_year"] >= anio_min
        ]

    if anio_max is not None:
        resultados = [
            a
            for a in resultados
            if a.get("release_year") is not None and a["release_year"] <= anio_max
        ]

    if rating_min is not None:
        resultados = [
            a
            for a in resultados
            if a.get("rating") is not None and a["rating"] >= rating_min
        ]

    if not resultados:
        return "No encontré animes con esos criterios."

    return json.dumps(resultados[:20], ensure_ascii=False, indent=2)
