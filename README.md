# Anime Advisor - Agente de IA con Strands + MiniMax M2.7

Sistema de recomendación de anime construido con **Strands Agents**, **API MiniMax M2.7** y **ChromaDB** para búsqueda semántica. Incluye servidor MCP propio con 4 herramientas de consulta.

## Características

- **18,495 animes** en la base de datos con información de géneros, estudios, ratings, años, descripciones
- **Búsqueda semántica** con embeddings de MiniMax y ChromaDB
- **12 herramientas custom** para buscar, recomendar y analizar
- **Servidor MCP propio** con 4 tools adicionales
- **Memoria persistente** entre conversaciones (FileSessionManager)
- **Perfil de usuario** que guarda gustos, animes vistos/favoritos/excluidos

## Requisitos

- Python 3.10+
- API key de MiniMax ([obtener aquí](https://platform.minimaxi.com/))

## Instalación

```bash
cd nerdearla-agente-aws

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

Edita el archivo `.env` y agrega tu API key de MiniMax:

```bash
MINIMAX_API_KEY=tu_api_key_aqui
```

## Uso

```bash
source .venv/bin/activate
python anime_agent.py
```

En la primera ejecución el sistema indexará los 18,495 animes para búsqueda semántica (puede tardar varios minutos).

### Ejemplo de conversación

```
>>> Hola! Me encanta el anime de acción y los estudios como MAPPA y Wit Studio. Mis favoritos son Demon Slayer y Attack on Titan.

>>> Armame una lista de 5 animes que te parece que me pueden gustar.
```

## Estructura del proyecto

```
nerdearla-agente-aws/
├── anime_agent.py          # Agente principal con Strands
├── mcp_server.py           # Servidor MCP propio
├── mcp.json                # Configuración MCP
├── Anime.csv               # Dataset original (Kaggle)
├── data/
│   ├── anime_procesado.json  # Animes parseados
│   └── preferencias.json     # Perfil del usuario
├── services/
│   ├── embedding.py          # Integración MiniMax Embeddings
│   └── chromadb.py           # Vector store
├── tools/
│   ├── busqueda.py           # buscar_anime()
│   ├── recommend.py           # recomendar_anime(), RAG
│   ├── estadisticas.py        # analizar_estadisticas()
│   └── preferencias.py        # Perfil de usuario
├── sessions/                # Memorias de conversación
└── requirements.txt
```

## Herramientas disponibles

### Tools propias del agente

| Herramienta | Descripción |
|------------|-------------|
| `buscar_anime` | Filtra por género, estudio, tipo, año, rating |
| `recomendar_anime` | Búsqueda semántica por descripción |
| `recomendar_por_tags` | Recomendaciones por etiquetas |
| `analizar_estadisticas` | Estadísticas del dataset |
| `ranking_top` | Top animes por rating |
| `obtener_perfil_usuario` | Ver preferencias guardadas |
| `agregar_genero_favorito` | Guardar género偏好 |
| `agregar_estudio_favorito` | Guardar estudio偏好 |
| `marcar_anime_visto` | Marcar anime como visto |
| `marcar_anime_favorito` | Marcar anime como favorito |
| `excluir_anime_por_nombre` | Excluir anime de recomendaciones |
| `actualizar_descripcion_perfil` | Actualizar perfil textual |

### Tools MCP (servidor propio)

| Herramienta | Descripción |
|------------|-------------|
| `anime_buscar` | Búsqueda avanzada con múltiples filtros |
| `anime_top` | Top N animes por rating |
| `anime_random` | Animes aleatorios para explorar |
| `anime_info` | Información detallada de un anime |

## Tickets Nerdearla

Este proyecto implementa las siguientes features para participación:

- [x] Custom tools con `@tool` → **+1 ticket**
- [x] Session management (memoria) → **+1 ticket**
- [x] Servidor MCP propio → **+1 ticket**

## Dataset

Datos tomados de [Anime Dataset en Kaggle](https://www.kaggle.com/datasets/unibahmad/anime-dataset) por UniBahmad.

## Licencia

MIT