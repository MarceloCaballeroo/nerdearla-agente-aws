import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from strands import Agent
from strands.models.openai import OpenAIModel
from strands.session.file_session_manager import FileSessionManager
from strands.tools.mcp import MCPClient, MCPAgentTool
from mcp.client.stdio import StdioServerParameters, stdio_client
from dotenv import load_dotenv

from tools.busqueda import buscar_anime
from tools.recommend import recomendar_anime, indexar_animes, recomendar_por_tags
from tools.estadisticas import analizar_estadisticas, ranking_top
from tools.preferencias import (
    obtener_perfil_usuario,
    agregar_genero_favorito,
    agregar_estudio_favorito,
    marcar_anime_visto,
    marcar_anime_favorito,
    excluir_anime_por_nombre,
    actualizar_descripcion_perfil,
)

load_dotenv()

API_KEY = os.getenv("MINIMAX_API_KEY", "")
if not API_KEY:
    print("ERROR: MINIMAX_API_KEY no está configurada en el archivo .env")
    print("Edita el archivo .env y agrega tu API key:")
    print("MINIMAX_API_KEY=tu_api_key_aqui")
    sys.exit(1)

modelo = OpenAIModel(
    model_id="MiniMax-M2.7", api_key=API_KEY, base_url="https://api.minimax.io/v1"
)

session_manager = FileSessionManager(
    session_id="anime-advisor", storage_dir="./sessions"
)

SYSTEM_PROMPT = """Eres un experto en anime con conocimiento extenso del catálogo de animes.

Tu rol es ayudar al usuario a descubrir, recomendar y explorar animes basados en sus preferencias personales.

INSTRUCCIONES DE FUNCIONAMIENTO:

1. RECOPILACIÓN DE PREFERENCIAS (al inicio):
   - Si no conoces los gustos del usuario, PREGÚNTALE sobre:
     * Géneros de anime que le gustan (acción, romance, shoujo, seinen, etc.)
     * Estudios cuyo trabajo admira (MAPPA, Wit Studio, Bones, etc.)
     * Tipos de anime que prefiere (TV, Movies, OVA, etc.)
     * Si tiene animes favoritos específicos
   - Guarda estas preferencias con las funciones de preferencias correspondientes
   - Usa la información guardada para personalizar recomendaciones

2. FUNCIONES DISPONIBLES:
   - buscar_anime: Filtra por género, estudio, tipo, año, rating
   - recomendar_anime: Búsqueda semántica por descripción del usuario
   - recomendar_por_tags: Recomendaciones basadas en etiquetas específicas
   - analizar_estadisticas: Estadísticas del dataset o por género
   - ranking_top: Top animes por rating
   - obtener_perfil_usuario: Ver preferencias guardadas
   - agregar_genero_favorito / agregar_estudio_favorito
   - marcar_anime_visto / marcar_anime_favorito / excluir_anime_por_nombre
   - actualizar_descripcion_perfil
   - anime_buscar: Búsqueda vía MCP server
   - anime_top: Top animes vía MCP server
   - anime_random: Recomendaciones aleatorias vía MCP server
   - anime_info: Detalle de anime específico vía MCP server

3. FORMATO DE RESPUESTAS:
   - Usa bullet points y formato legible
   - Incluye rating y año cuando esté disponible
   - Sugiere siempre próximos pasos: buscar más, marcar como visto, etc.

4. RECOMENDACIONES INTELIGENTES:
   - Combina preferencias guardadas + búsqueda semántica
   - Sugiere animes similares a los favoritos del usuario
   - Evita sugerir animes ya marcados como excluidos
   - Considera el rating como factor secundario (no solo mejores rating)

COMIENZA preguntando al usuario sobre sus gustos si aún no conoces sus preferencias."""


def crear_mcp_tools():
    server_params = StdioServerParameters(
        command="python", args=["mcp_server.py"], cwd=str(Path(__file__).parent)
    )

    def get_stdio_transport():
        return stdio_client(server_params)

    mcp_client = MCPClient(transport_callable=get_stdio_transport, prefix="anime_")

    mcp_tools = mcp_client.list_tools()
    agent_tools = [
        MCPAgentTool(mcp_tool=tool, mcp_client=mcp_client) for tool in mcp_tools
    ]

    return agent_tools, mcp_client


def inicializar_sistema():
    print("=" * 60)
    print("  Anime Advisor - Sistema de Recomendación de Anime")
    print("=" * 60)
    print()

    from services.chromadb import collection_exists

    if not collection_exists("anime_embeddings"):
        print("[*] Primera ejecución detectada...")
        print("[*] Indexando animes para búsqueda semántica...")
        print("[*] Esto puede tomar varios minutos...")
        indexar_animes()
        print("[*] Indexado completado!")
    else:
        print("[*] Base de datos de embeddings ya existe.")

    print()
    print("[*] Sistema listo. El agente preguntará por tus gustos.")
    print("[*] Escribe 'salir' para terminar.")
    print()


if __name__ == "__main__":
    inicializar_sistema()

    print("-" * 60)
    print("CONVERSACIÓN:")
    print("-" * 60)

    agent_tools = []
    mcp_client_instance = None

    try:
        print("[*] Conectando con MCP server de anime...")
        mcp_tools, mcp_client_instance = crear_mcp_tools()
        agent_tools = mcp_tools
        print(f"[*] MCP conectado: {len(mcp_tools)} herramientas disponibles")
    except Exception as e:
        print(f"[!] MCP no disponible: {e}")
        print("[*] Continuando sin MCP...")

    all_tools = [
        buscar_anime,
        recomendar_anime,
        recomendar_por_tags,
        analizar_estadisticas,
        ranking_top,
        obtener_perfil_usuario,
        agregar_genero_favorito,
        agregar_estudio_favorito,
        marcar_anime_visto,
        marcar_anime_favorito,
        excluir_anime_por_nombre,
        actualizar_descripcion_perfil,
    ] + agent_tools

    agent = Agent(
        model=modelo,
        system_prompt=SYSTEM_PROMPT,
        tools=all_tools,
        session_manager=session_manager,
    )

    primera_pregunta = True
    while True:
        try:
            if primera_pregunta:
                user_input = input(">>> ")
                primera_pregunta = False
            else:
                user_input = input(">>> ")

            if user_input.lower() in ["salir", "exit", "quit", "q"]:
                print("\n¡Hasta luego! Sigue explorando anime.")
                break

            if not user_input.strip():
                continue

            response = agent(user_input)
            print("\n---")
            print(response)
            print("---")

        except KeyboardInterrupt:
            print("\n\n¡Hasta luego! Sigue explorando anime.")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback

            traceback.print_exc()
            print("Intenta de nuevo.")
