import json
from pathlib import Path
from typing import Optional

BIBLIOTECA = Path(__file__).parent / "data" / "anime_procesado.json"
PREFERENCIAS = Path(__file__).parent / "data" / "preferencias.json"
_biblioteca = None


def get_biblioteca():
    global _biblioteca
    if _biblioteca is None:
        with open(BIBLIOTECA, encoding="utf-8") as f:
            _biblioteca = json.load(f)
    return _biblioteca


def get_preferencias():
    if not PREFERENCIAS.exists():
        return {
            "generos_favoritos": [],
            "estudios_favoritos": [],
            "animes_vistos": [],
            "animes_favoritos": [],
            "animes_excluidos": [],
            "descripcion_perfil": "",
        }
    with open(PREFERENCIAS, encoding="utf-8") as f:
        return json.load(f)


def save_preferencias(prefs):
    PREFERENCIAS.parent.mkdir(parents=True, exist_ok=True)
    with open(PREFERENCIAS, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)


def filter_animes(
    genero="",
    estudio="",
    tipo="",
    anio_min=None,
    anio_max=None,
    rating_min=None,
    nombre="",
):
    results = get_biblioteca()
    if nombre:
        results = [a for a in results if nombre.lower() in a["name"].lower()]
    if genero:
        results = [
            a
            for a in results
            if any(genero.lower() in tag.lower() for tag in a.get("tags", []))
        ]
    if estudio:
        results = [
            a
            for a in results
            if any(estudio.lower() in s.lower() for s in a.get("studios", []))
        ]
    if tipo:
        results = [a for a in results if tipo.lower() in a.get("type", "").lower()]
    if anio_min is not None:
        results = [
            a
            for a in results
            if a.get("release_year") and a["release_year"] >= anio_min
        ]
    if anio_max is not None:
        results = [
            a
            for a in results
            if a.get("release_year") and a["release_year"] <= anio_max
        ]
    if rating_min is not None:
        results = [a for a in results if a.get("rating") and a["rating"] >= rating_min]
    return results[:20] if results else None


from strands import tool


@tool
def buscar_anime(
    genero: str = "",
    estudio: str = "",
    tipo: str = "",
    anio_min: Optional[int] = None,
    anio_max: Optional[int] = None,
    rating_min: Optional[float] = None,
) -> str:
    """Busca animes por genero, estudio, tipo, anio y rating. Retorna hasta 20 resultados."""
    results = filter_animes(genero, estudio, tipo, anio_min, anio_max, rating_min)
    return (
        json.dumps(results, ensure_ascii=False, indent=2)
        if results
        else "No encontrado"
    )


@tool
def ranking_top(n: int = 20, genero: str = "") -> str:
    """Top N animes por rating. Filtrar por genero opcional."""
    biblioteca = get_biblioteca()
    if genero:
        biblioteca = [
            a
            for a in biblioteca
            if any(genero.lower() in tag.lower() for tag in a.get("tags", []))
        ]
    ranked = sorted(
        [a for a in biblioteca if a.get("rating")],
        key=lambda x: x["rating"],
        reverse=True,
    )[:n]
    return json.dumps(
        [
            {
                "rank": a["rank"],
                "name": a["name"],
                "rating": a["rating"],
                "year": a.get("release_year"),
                "tags": a.get("tags", [])[:5],
            }
            for a in ranked
        ],
        ensure_ascii=False,
        indent=2,
    )


@tool
def analizar_estadisticas(genero: str = "") -> str:
    """Estadisticas del dataset o filtrado por genero."""
    biblioteca = get_biblioteca()
    if genero:
        biblioteca = [
            a
            for a in biblioteca
            if any(genero.lower() in tag.lower() for tag in a.get("tags", []))
        ]
    ratings = [a["rating"] for a in biblioteca if a.get("rating")]
    years = [a["release_year"] for a in biblioteca if a.get("release_year")]
    estudios = {}
    for a in biblioteca:
        for s in a.get("studios", []):
            estudios[s] = estudios.get(s, 0) + 1
    tags = {}
    for a in biblioteca:
        for t in a.get("tags", []):
            tags[t] = tags.get(t, 0) + 1
    return json.dumps(
        {
            "total": len(biblioteca),
            "rating_promedio": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "anio_rango": f"{min(years)}-{max(years)}" if years else "N/A",
            "top_estudios": dict(
                sorted(estudios.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "top_tags": dict(
                sorted(tags.items(), key=lambda x: x[1], reverse=True)[:15]
            ),
        },
        ensure_ascii=False,
        indent=2,
    )


@tool
def obtener_perfil_usuario() -> str:
    """Ver preferencias guardadas del usuario."""
    return json.dumps(get_preferencias(), ensure_ascii=False, indent=2)


@tool
def agregar_genero_favorito(generos: list[str]) -> str:
    """Agrega generos favoritos a tu perfil."""
    prefs = get_preferencias()
    for g in generos:
        g = g.strip()
        if g and g not in prefs["generos_favoritos"]:
            prefs["generos_favoritos"].append(g)
    save_preferencias(prefs)
    return json.dumps({"generos": prefs["generos_favoritos"]}, ensure_ascii=False)


@tool
def agregar_estudio_favorito(estudios: list[str]) -> str:
    """Agrega estudios favoritos a tu perfil."""
    prefs = get_preferencias()
    for e in estudios:
        e = e.strip()
        if e and e not in prefs["estudios_favoritos"]:
            prefs["estudios_favoritos"].append(e)
    save_preferencias(prefs)
    return json.dumps({"estudios": prefs["estudios_favoritos"]}, ensure_ascii=False)


@tool
def marcar_anime_visto(rank: int, nombre: str) -> str:
    """Marca un anime como visto."""
    prefs = get_preferencias()
    entry = {"rank": rank, "name": nombre}
    if entry not in prefs["animes_vistos"]:
        prefs["animes_vistos"].append(entry)
    save_preferencias(prefs)
    return json.dumps({"vistos": len(prefs["animes_vistos"])}, ensure_ascii=False)


@tool
def marcar_anime_favorito(rank: int, nombre: str) -> str:
    """Marca un anime como favorito."""
    prefs = get_preferencias()
    entry = {"rank": rank, "name": nombre}
    if entry not in prefs["animes_favoritos"]:
        prefs["animes_favoritos"].append(entry)
    save_preferencias(prefs)
    return json.dumps({"favoritos": len(prefs["animes_favoritos"])}, ensure_ascii=False)


@tool
def excluir_anime_por_nombre(nombre: str) -> str:
    """Excluye un anime de las recomendaciones."""
    prefs = get_preferencias()
    nombre_lower = nombre.lower()
    if nombre_lower not in prefs["animes_excluidos"]:
        prefs["animes_excluidos"].append(nombre_lower)
    prefs["animes_vistos"] = [
        a for a in prefs["animes_vistos"] if nombre_lower not in a["name"].lower()
    ]
    prefs["animes_favoritos"] = [
        a for a in prefs["animes_favoritos"] if nombre_lower not in a["name"].lower()
    ]
    save_preferencias(prefs)
    return json.dumps(
        {"excluido": nombre, "total": len(prefs["animes_excluidos"])},
        ensure_ascii=False,
    )
