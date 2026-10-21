# Anime Advisor

Agente conversacional de recomendación de anime, construido con [Strands Agents](https://strandsagents.com/) (SDK de código abierto de AWS) durante un evento de **Nerdearla Chile 2026**.

El agente conversa con el usuario, consulta un catálogo de **18.495 animes** mediante herramientas propias, recuerda sus gustos entre sesiones y propone recomendaciones personalizadas.

## Qué demuestra

- **Agentes de IA con tool use:** el modelo decide cuándo llamar a cada una de las 9 herramientas (`@tool`) para filtrar, rankear y analizar el catálogo.
- **Memoria:** el perfil del usuario (géneros, estudios, vistos, favoritos y excluidos) se persiste en disco, y la conversación se conserva con `FileSessionManager`.
- **Modelo intercambiable:** usa la interfaz compatible con OpenAI de Strands, con MiniMax M2.7 como modelo por defecto. Cambiar de proveedor requiere modificar solo `model_id` y `base_url` en `anime_agent.py`.

## Arquitectura

```
Usuario ──► Agente (Strands) ──► Modelo (MiniMax M2.7, API compatible con OpenAI)
                │
                ├─► tools.py ──► data/anime_procesado.json   (catálogo)
                │            └─► data/preferencias.json      (perfil del usuario)
                └─► FileSessionManager ──► sessions/         (memoria de conversación)
```

| Archivo | Función |
|---|---|
| `anime_agent.py` | Agente principal y bucle de conversación |
| `tools.py` | Las 9 herramientas del agente |
| `scripts/procesar_dataset.py` | Convierte el CSV original en `data/anime_procesado.json` |

## Herramientas

| Herramienta | Descripción |
|---|---|
| `buscar_anime` | Filtra por género, estudio, tipo, año y rating |
| `ranking_top` | Top N por rating |
| `analizar_estadisticas` | Estadísticas del catálogo |
| `obtener_perfil_usuario` | Muestra las preferencias guardadas |
| `agregar_genero_favorito` | Guarda un género favorito |
| `agregar_estudio_favorito` | Guarda un estudio favorito |
| `marcar_anime_visto` | Marca un anime como visto |
| `marcar_anime_favorito` | Marca un anime como favorito |
| `excluir_anime_por_nombre` | Lo excluye de futuras recomendaciones |

## Cómo ejecutarlo

Requiere Python 3.10 o superior y una API key de MiniMax.

```bash
python -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # y completa MINIMAX_API_KEY

# Solo si quieres regenerar el catálogo desde el CSV original
python scripts/procesar_dataset.py Anime.csv data/anime_procesado.json

python anime_agent.py
```

Escribe `salir` para terminar. La API key vive en `.env`, que está excluido del repositorio.

## Alcance y límites

Es un proyecto de evento: prioriza un agente funcional de punta a punta por sobre pruebas automatizadas o una interfaz gráfica. Se descartó la búsqueda semántica con embeddings por no contar con la API necesaria durante el evento, por lo que las recomendaciones se basan en filtros estructurados y en el razonamiento del modelo.

## Autor

Marcelo Caballero Olave · [LinkedIn](https://www.linkedin.com/in/marcelo-caballero-olave) · [Portafolio](https://marcelocaballero.me/)
