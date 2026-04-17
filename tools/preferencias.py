import json
from pathlib import Path
from typing import Optional

PREFERENCIAS_PATH = Path(__file__).parent.parent / "data" / "preferencias.json"


def cargar_preferencias() -> dict:
    if not PREFERENCIAS_PATH.exists():
        return {
            "generos_favoritos": [],
            "estudios_favoritos": [],
            "animes_vistos": [],
            "animes_favoritos": [],
            "animes_excluidos": [],
            "descripcion_perfil": "",
        }
    with open(PREFERENCIAS_PATH, encoding="utf-8") as f:
        return json.load(f)


def guardar_preferencias(preferencias: dict):
    PREFERENCIAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PREFERENCIAS_PATH, "w", encoding="utf-8") as f:
        json.dump(preferencias, f, ensure_ascii=False, indent=2)


def obtener_perfil_usuario() -> str:
    prefs = cargar_preferencias()
    return json.dumps(prefs, ensure_ascii=False, indent=2)


def agregar_genero_favorito(generos: list[str]) -> str:
    prefs = cargar_preferencias()
    for g in generos:
        g_clean = g.strip()
        if g_clean and g_clean not in prefs["generos_favoritos"]:
            prefs["generos_favoritos"].append(g_clean)
    guardar_preferencias(prefs)
    return json.dumps(
        {"generos_favoritos": prefs["generos_favoritos"]}, ensure_ascii=False, indent=2
    )


def agregar_estudio_favorito(estudios: list[str]) -> str:
    prefs = cargar_preferencias()
    for e in estudios:
        e_clean = e.strip()
        if e_clean and e_clean not in prefs["estudios_favoritos"]:
            prefs["estudios_favoritos"].append(e_clean)
    guardar_preferencias(prefs)
    return json.dumps(
        {"estudios_favoritos": prefs["estudios_favoritos"]},
        ensure_ascii=False,
        indent=2,
    )


def marcar_anime_visto(rank: int, nombre: str) -> str:
    prefs = cargar_preferencias()
    entry = {"rank": rank, "name": nombre}
    if entry not in prefs["animes_vistos"]:
        prefs["animes_vistos"].append(entry)
    guardar_preferencias(prefs)
    return json.dumps(
        {"animes_vistos_count": len(prefs["animes_vistos"])}, ensure_ascii=False
    )


def marcar_anime_favorito(rank: int, nombre: str) -> str:
    prefs = cargar_preferencias()
    entry = {"rank": rank, "name": nombre}
    if entry not in prefs["animes_favoritos"]:
        prefs["animes_favoritos"].append(entry)
    guardar_preferencias(prefs)
    return json.dumps(
        {"animes_favoritos_count": len(prefs["animes_favoritos"])}, ensure_ascii=False
    )


def excluir_anime_por_nombre(nombre: str) -> str:
    prefs = cargar_preferencias()
    nombre_lower = nombre.lower()
    if nombre_lower not in prefs["animes_excluidos"]:
        prefs["animes_excluidos"].append(nombre_lower)
    prefs["animes_vistos"] = [
        a for a in prefs["animes_vistos"] if nombre_lower not in a["name"].lower()
    ]
    prefs["animes_favoritos"] = [
        a for a in prefs["animes_favoritos"] if nombre_lower not in a["name"].lower()
    ]
    guardar_preferencias(prefs)
    return json.dumps(
        {"animes_excluidos": prefs["animes_excluidos"], "excluido": nombre},
        ensure_ascii=False,
        indent=2,
    )


def actualizar_descripcion_perfil(descripcion: str) -> str:
    prefs = cargar_preferencias()
    prefs["descripcion_perfil"] = descripcion
    guardar_preferencias(prefs)
    return json.dumps({"descripcion_perfil": descripcion}, ensure_ascii=False, indent=2)
