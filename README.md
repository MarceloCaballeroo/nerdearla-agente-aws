# Anime Advisor

Sistema de recomendación de anime con **Strands Agents** y **MiniMax M2.7**.

## Estructura

```
├── anime_agent.py     # Agente principal (70 lineas)
├── tools.py            # 9 tools @tool
├── scripts/
│   └── procesar_dataset.py
├── data/
│   └── anime_procesado.json  # 18,495 animes
└── sessions/           # FileSessionManager
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
# Primera vez: procesar dataset
python scripts/procesar_dataset.py Anime.csv data/anime_procesado.json

# Ejecutar agente
python anime_agent.py
```

## Tools (9)

| Herramienta | Descripción |
|------------|-------------|
| `buscar_anime` | Filtra por genero/estudio/tipo/año/rating |
| `ranking_top` | Top N por rating |
| `analizar_estadisticas` | Estadísticas del dataset |
| `obtener_perfil_usuario` | Ver preferencias guardadas |
| `agregar_genero_favorito` | Guardar géneros |
| `agregar_estudio_favorito` | Guardar estudios |
| `marcar_anime_visto` | Marcar como visto |
| `marcar_anime_favorito` | Marcar como favorito |
| `excluir_anime_por_nombre` | Excluir de recomendaciones |

## Tickets

- [x] Custom tools con `@tool` → +1 ticket
- [x] Session management (memoria) → +1 ticket