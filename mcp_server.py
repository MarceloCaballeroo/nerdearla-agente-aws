#!/usr/bin/env python3
import json
import sys
import os
from pathlib import Path
from typing import Any

ANIME_JSON = Path(__file__).parent / "data" / "anime_procesado.json"

_biblioteca = None


def get_biblioteca():
    global _biblioteca
    if _biblioteca is None:
        if ANIME_JSON.exists():
            with open(ANIME_JSON, encoding="utf-8") as f:
                _biblioteca = json.load(f)
        else:
            _biblioteca = []
    return _biblioteca


TOOLS = [
    {
        "name": "anime_buscar",
        "description": "Busca animes por criterios. Retorna hasta 15 resultados.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "genero": {
                    "type": "string",
                    "description": "Género (action, romance, horror, etc)",
                },
                "estudio": {
                    "type": "string",
                    "description": "Nombre del estudio (MAPPA, Wit Studio, etc)",
                },
                "tipo": {"type": "string", "description": "Tipo (TV, Movie, OVA, Web)"},
                "anio_min": {
                    "type": "integer",
                    "description": "Año mínimo de lanzamiento",
                },
                "rating_min": {"type": "number", "description": "Rating mínimo (0-5)"},
            },
        },
    },
    {
        "name": "anime_top",
        "description": "Obtiene el top de animes por rating.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "n": {
                    "type": "integer",
                    "description": "Cantidad a devolver",
                    "default": 10,
                },
                "genero": {
                    "type": "string",
                    "description": "Filtrar por género específico",
                },
            },
        },
    },
    {
        "name": "anime_random",
        "description": "Recomienda animes aleatorios interesante para explorar.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "n": {
                    "type": "integer",
                    "description": "Cantidad a devolver",
                    "default": 5,
                },
                "genero": {"type": "string", "description": "Género preferido"},
            },
        },
    },
    {
        "name": "anime_info",
        "description": "Obtiene información detallada de un anime por su nombre.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "nombre": {"type": "string", "description": "Nombre del anime a buscar"}
            },
        },
    },
]


def call_tool(name: str, arguments: dict) -> dict:
    biblioteca = get_biblioteca()

    if name == "anime_buscar":
        resultados = biblioteca
        if args.get("genero"):
            g = args["genero"].lower()
            resultados = [
                a
                for a in resultados
                if any(g in tag.lower() for tag in a.get("tags", []))
            ]
        if args.get("estudio"):
            e = args["estudio"].lower()
            resultados = [
                a
                for a in resultados
                if any(e in s.lower() for s in a.get("studios", []))
            ]
        if args.get("tipo"):
            resultados = [
                a
                for a in resultados
                if args["tipo"].lower() in a.get("type", "").lower()
            ]
        if args.get("anio_min"):
            resultados = [
                a
                for a in resultados
                if a.get("release_year") and a["release_year"] >= args["anio_min"]
            ]
        if args.get("rating_min"):
            resultados = [
                a
                for a in resultados
                if a.get("rating") and a["rating"] >= args["rating_min"]
            ]

        output = []
        for a in resultados[:15]:
            output.append(
                {
                    "rank": a["rank"],
                    "name": a["name"],
                    "rating": a.get("rating"),
                    "year": a.get("release_year"),
                    "studios": a.get("studios", []),
                    "tags": a.get("tags", [])[:8],
                }
            )
        return {
            "content": [
                {"type": "text", "text": json.dumps(output, ensure_ascii=False)}
            ]
        }

    elif name == "anime_top":
        n = args.get("n", 10)
        genero = args.get("genero", "")

        resultados = biblioteca
        if genero:
            g = genero.lower()
            resultados = [
                a
                for a in resultados
                if any(g in tag.lower() for tag in a.get("tags", []))
            ]

        ranked = sorted(
            [a for a in resultados if a.get("rating")],
            key=lambda x: x["rating"],
            reverse=True,
        )

        output = [
            {
                "rank": a["rank"],
                "name": a["name"],
                "rating": a["rating"],
                "year": a.get("release_year"),
            }
            for a in ranked[:n]
        ]
        return {
            "content": [
                {"type": "text", "text": json.dumps(output, ensure_ascii=False)}
            ]
        }

    elif name == "anime_random":
        import random

        n = args.get("n", 5)
        genero = args.get("genero", "")

        pool = biblioteca
        if genero:
            g = genero.lower()
            pool = [
                a for a in pool if any(g in tag.lower() for tag in a.get("tags", []))
            ]

        if not pool:
            pool = biblioteca

        seleccionados = random.sample(pool, min(n, len(pool)))
        output = [
            {
                "rank": a["rank"],
                "name": a["name"],
                "rating": a.get("rating"),
                "tags": a.get("tags", [])[:5],
            }
            for a in seleccionados
        ]
        return {
            "content": [
                {"type": "text", "text": json.dumps(output, ensure_ascii=False)}
            ]
        }

    elif name == "anime_info":
        nombre = args.get("nombre", "").lower()
        if not nombre:
            return {"content": [{"type": "text", "text": "Error: nombre requerido"}]}

        for a in biblioteca:
            if nombre in a.get("name", "").lower():
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "rank": a["rank"],
                                    "name": a["name"],
                                    "japanese_name": a.get("japanese_name", ""),
                                    "type": a.get("type", ""),
                                    "episodes": a.get("episodes"),
                                    "studios": a.get("studios", []),
                                    "tags": a.get("tags", []),
                                    "rating": a.get("rating"),
                                    "release_year": a.get("release_year"),
                                    "description": a.get("description", "")[:500],
                                },
                                ensure_ascii=False,
                            ),
                        }
                    ]
                }

        return {
            "content": [
                {"type": "text", "text": f"No encontré anime con nombre: {nombre}"}
            ]
        }

    return {"content": [{"type": "text", "text": f"Tool desconocida: {name}"}]}


def handle_request(request: dict) -> dict:
    method = request.get("method", "")
    params = request.get("params", {})

    if method == "tools/list":
        return {"tools": TOOLS}
    elif method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {})
        return call_tool(name, args)

    return {"error": f"Method not found: {method}"}


if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)
