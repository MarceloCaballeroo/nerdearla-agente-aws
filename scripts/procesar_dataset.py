import pandas as pd
import json
import re
import sys
import os
from pathlib import Path


def parse_anime_csv(csv_path: str, output_path: str) -> list[dict]:
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    animes = []
    current_anime = None

    for idx, row in df.iterrows():
        rank = row.get("Rank")
        name = row.get("Name")

        if pd.notna(rank) and pd.notna(name):
            if current_anime:
                animes.append(current_anime)

            tags_raw = row.get("Tags", "")
            tags = (
                [t.strip() for t in str(tags_raw).split(",") if t.strip()]
                if pd.notna(tags_raw)
                else []
            )

            studios_raw = row.get("Studio", "")
            studios = (
                [s.strip() for s in str(studios_raw).split(",") if s.strip()]
                if pd.notna(studios_raw)
                else []
            )

            voice_actors_raw = row.get("Voice_actors", "")
            voice_actors = []
            if pd.notna(voice_actors_raw):
                for va in str(voice_actors_raw).split(","):
                    if ":" in va:
                        parts = va.split(":")
                        character = parts[0].strip()
                        actor = ":".join(parts[1:]).strip()
                        voice_actors.append({"character": character, "actor": actor})

            description_raw = row.get("Description", "")
            description = ""
            if pd.notna(description_raw):
                desc_match = re.search(r"'([^']*)'", str(description_raw))
                description = (
                    desc_match.group(1)
                    if desc_match
                    else str(description_raw).strip("'\"")
                )

            content_warning_raw = row.get("Content_Warning", "")
            content_warnings = []
            if pd.notna(content_warning_raw):
                for cw in str(content_warning_raw).split(","):
                    cw = cw.strip().strip("'\"")
                    if cw:
                        content_warnings.append(cw)

            current_anime = {
                "rank": int(rank) if pd.notna(rank) else None,
                "name": str(name).strip(),
                "japanese_name": str(row.get("Japanese_name", "")).strip()
                if pd.notna(row.get("Japanese_name"))
                else "",
                "type": str(row.get("Type", "")).strip()
                if pd.notna(row.get("Type"))
                else "",
                "episodes": float(row.get("Episodes"))
                if pd.notna(row.get("Episodes"))
                else None,
                "studios": studios,
                "release_season": str(row.get("Release_season", "")).strip()
                if pd.notna(row.get("Release_season"))
                else "",
                "tags": tags,
                "rating": float(row.get("Rating"))
                if pd.notna(row.get("Rating"))
                else None,
                "release_year": int(float(row.get("Release_year")))
                if pd.notna(row.get("Release_year"))
                else None,
                "end_year": int(float(row.get("End_year")))
                if pd.notna(row.get("End_year"))
                else None,
                "description": description,
                "content_warnings": content_warnings,
                "related_manga": str(row.get("Related_Mange", "")).strip()
                if pd.notna(row.get("Related_Mange"))
                else "",
                "related_anime": str(row.get("Related_anime", "")).strip()
                if pd.notna(row.get("Related_anime"))
                else "",
                "voice_actors": voice_actors,
                "staff": [],
            }
        else:
            if current_anime is not None:
                staff_val = row.get("Staff")
                if pd.notna(staff_val):
                    staff_str = str(staff_val)
                    if ":" in staff_str:
                        parts = staff_str.split(",", 1)
                        role = parts[0].strip()
                        person = parts[1].strip() if len(parts) > 1 else ""
                        if role and person:
                            current_anime["staff"].append({role: person})

    if current_anime:
        animes.append(current_anime)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(animes, f, ensure_ascii=False, indent=2)

    print(f"Procesados {len(animes)} animes -> {output_path}")
    return animes


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "Anime.csv"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "data/anime_procesado.json"
    force = "--force" in sys.argv or "-f" in sys.argv

    csv_file = Path(csv_path)
    json_file = Path(output_path)

    if not csv_file.exists():
        print(f"ERROR: CSV no encontrado: {csv_path}")
        sys.exit(1)

    if json_file.exists() and not force:
        print(f"[*] {json_file.name} ya existe. Usar --force para re-procesar.")
        sys.exit(0)

    if json_file.exists() and force:
        print(f"[*] Forzando re-procesamiento de {csv_path}...")

    parse_anime_csv(str(csv_file), str(json_file))


if __name__ == "__main__":
    main()
