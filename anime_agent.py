import os, sys
from pathlib import Path
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.session.file_session_manager import FileSessionManager
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from tools import (
    buscar_anime,
    ranking_top,
    analizar_estadisticas,
    obtener_perfil_usuario,
    agregar_genero_favorito,
    agregar_estudio_favorito,
    marcar_anime_visto,
    marcar_anime_favorito,
    excluir_anime_por_nombre,
)

load_dotenv()

API_KEY = os.getenv("MINIMAX_API_KEY", "")
if not API_KEY:
    print("ERROR: MINIMAX_API_KEY no configurada en .env")
    sys.exit(1)

modelo = OpenAIModel(
    model_id="MiniMax-M2.7",
    client_args={"api_key": API_KEY, "base_url": "https://api.minimax.io/v1"},
)

session_manager = FileSessionManager(
    session_id="anime-advisor", storage_dir="./sessions"
)

SYSTEM_PROMPT = """Eres un experto en anime. Pregunta al usuario sus gustos (géneros, estudios, tipos de anime) y usa las herramientas para dar recomendaciones personalizadas y guardar sus preferencias."""

if __name__ == "__main__":
    print("=" * 50)
    print("  Anime Advisor")
    print("=" * 50)

    anime_json = Path("data/anime_procesado.json")
    if not anime_json.exists():
        print("ERROR: Ejecuta primero: python scripts/procesar_dataset.py")
        sys.exit(1)

    print("[*] Sistema listo!\n")
    print("CONVERSACIÓN (escribe 'salir' para terminar)")
    print("-" * 50)

    agent = Agent(
        model=modelo,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            buscar_anime,
            ranking_top,
            analizar_estadisticas,
            obtener_perfil_usuario,
            agregar_genero_favorito,
            agregar_estudio_favorito,
            marcar_anime_visto,
            marcar_anime_favorito,
            excluir_anime_por_nombre,
        ],
        session_manager=session_manager,
    )

    while True:
        try:
            user_input = input(">>> ")
            if user_input.lower() in ["salir", "exit", "quit"]:
                break
            if not user_input.strip():
                continue
            print("\n---\n" + agent(user_input) + "\n---")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

    print("\n¡Hasta luego!")
