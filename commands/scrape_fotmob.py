#!/usr/bin/env python3
"""
Scraper de partidos de FotMob.

Extrae estadisticas, shotmap, alineaciones y eventos de un partido de FotMob
usando el patron __NEXT_DATA__ de Next.js. Exporta los datos en CSVs compatibles
con las operaciones del homework (mapa de tiros, estadisticas de partido, alineaciones).

Uso:
    python scrape_fotmob.py <match_id> [--output-dir <directorio>]

Ejemplo:
    python scrape_fotmob.py 5169244
    python scrape_fotmob.py 5169244 --output-dir ../data/fotmob
"""

import argparse
import json
import os
import re
import sys

import pandas as pd
from requests_html import HTMLSession
from fake_useragent import UserAgent


def fetch_match_html(match_id: int) -> str:
    """Descarga el HTML del partido de FotMob y extrae el JSON de __NEXT_DATA__."""
    ua = UserAgent()
    session = HTMLSession()
    # /match/<id> redirige automaticamente a la URL completa con slug
    url = f"https://www.fotmob.com/match/{match_id}"
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",
    }

    response = session.get(url, headers=headers, timeout=20)
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code} al acceder a {url}")

    pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
    match = re.search(pattern, response.text, re.DOTALL | re.IGNORECASE)
    if not match:
        raise RuntimeError("No se encontro el bloque __NEXT_DATA__ en el HTML")

    return json.loads(match.group(1).strip())


def extract_content(json_data: dict) -> dict:
    """Navega al objeto 'content' dentro de la estructura de Next.js."""
    return json_data["props"]["pageProps"]["content"]


def extract_match_info(content: dict) -> dict:
    """Extrae informacion basica del partido (equipos, resultado, fecha)."""
    lineup = content.get("lineup", {})
    home_team = lineup.get("homeTeam", {}).get("name", "Local")
    away_team = lineup.get("awayTeam", {}).get("name", "Visitante")

    # Buscar resultado en los eventos (ultimo evento con score)
    match_facts = content.get("matchFacts", {})
    events = match_facts.get("events", {}).get("events", [])
    home_score, away_score = None, None
    for event in reversed(events):
        if event.get("homeScore") is not None:
            home_score = event.get("homeScore")
            away_score = event.get("awayScore")
            break

    # Info del partido
    infobox = match_facts.get("infoBox", {})

    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_score": home_score,
        "away_score": away_score,
        "infobox": infobox,
    }


def extract_match_stats(content: dict) -> pd.DataFrame:
    """Extrae estadisticas del partido (todas las secciones) como DataFrame."""
    stats_data = content.get("stats", {})
    periods = stats_data.get("Periods", {})
    stats_all = periods.get("All", {}).get("stats", [])

    rows = []
    for section in stats_all:
        section_name = section.get("title")
        for item in section.get("stats", []):
            values = item.get("stats", [])
            if values == [None, None]:
                continue
            rows.append({
                "seccion": section_name,
                "metrica": item.get("title"),
                "clave": item.get("key"),
                "local": values[0] if isinstance(values, list) and len(values) > 0 else None,
                "visitante": values[1] if isinstance(values, list) and len(values) > 1 else None,
                "formato": item.get("format", ""),
            })

    return pd.DataFrame(rows)


def extract_shotmap(content: dict) -> pd.DataFrame:
    """Extrae el shotmap (mapa de tiros) con coordenadas y xG por tiro."""
    shotmap = content.get("shotmap", {})
    shots = shotmap.get("shots", [])

    if not shots:
        return pd.DataFrame()

    df = pd.json_normalize(shots)
    return df


def extract_lineups(content: dict) -> pd.DataFrame:
    """Extrae alineaciones de ambos equipos con posiciones y ratings."""
    lineup = content.get("lineup", {})
    rows = []

    for side, key in [("local", "homeTeam"), ("visitante", "awayTeam")]:
        team_data = lineup.get(key, {})
        team_name = team_data.get("name", side)

        def parse_player(player, is_starter):
            rating_raw = player.get("rating")
            if isinstance(rating_raw, dict):
                rating = rating_raw.get("num", None)
            else:
                rating = rating_raw

            h_layout = player.get("horizontalLayout", {})
            v_layout = player.get("verticalLayout", {})

            return {
                "equipo": team_name,
                "lado": side,
                "jugador": player.get("name", ""),
                "id": player.get("id", ""),
                "dorsal": player.get("shirtNumber", ""),
                "posicion_id": player.get("positionId", ""),
                "titular": is_starter,
                "rating": rating,
                "layout_x": h_layout.get("x") if isinstance(h_layout, dict) else None,
                "layout_y": h_layout.get("y") if isinstance(h_layout, dict) else None,
            }

        for player in team_data.get("starters", []):
            rows.append(parse_player(player, True))

        for player in team_data.get("subs", []):
            rows.append(parse_player(player, False))

    return pd.DataFrame(rows)


def extract_events(content: dict) -> pd.DataFrame:
    """Extrae eventos del partido (goles, tarjetas, sustituciones)."""
    match_facts = content.get("matchFacts", {})
    events_data = match_facts.get("events", {})

    if not events_data or not isinstance(events_data, dict):
        return pd.DataFrame()

    events = events_data.get("events", [])
    if not events:
        return pd.DataFrame()

    rows = []
    for event in events:
        player = event.get("player", {})
        rows.append({
            "minuto": event.get("time", ""),
            "minuto_extra": event.get("overloadTime", None),
            "tipo": event.get("type", ""),
            "jugador": player.get("name", "") if isinstance(player, dict) else "",
            "jugador_id": player.get("id", "") if isinstance(player, dict) else "",
            "marcador_local": event.get("homeScore", None),
            "marcador_visitante": event.get("awayScore", None),
        })

    return pd.DataFrame(rows)


def extract_player_stats(content: dict) -> pd.DataFrame:
    """Extrae estadisticas individuales de jugadores si estan disponibles."""
    player_stats = content.get("playerStats", {})

    if not player_stats:
        return pd.DataFrame()

    rows = []
    for player_id, player_data in player_stats.items():
        if not isinstance(player_data, dict):
            continue

        row = {
            "player_id": player_data.get("id", player_id),
            "jugador": player_data.get("name", ""),
            "equipo": player_data.get("teamName", ""),
            "dorsal": player_data.get("shirtNumber", ""),
            "posicion_id": player_data.get("positionId", ""),
            "es_portero": player_data.get("isGoalkeeper", False),
        }

        # stats es una lista de secciones, cada seccion tiene un dict de metricas
        for section in player_data.get("stats", []):
            section_stats = section.get("stats", {})
            if isinstance(section_stats, dict):
                for stat_name, stat_data in section_stats.items():
                    if isinstance(stat_data, dict):
                        stat_obj = stat_data.get("stat", {})
                        if isinstance(stat_obj, dict):
                            row[stat_name] = stat_obj.get("value", None)

        rows.append(row)

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Scraper de partidos de FotMob — exporta datos en CSV"
    )
    parser.add_argument("match_id", type=int, help="ID del partido en FotMob (ej: 5169244)")
    parser.add_argument(
        "--output-dir", "-o", default=".",
        help="Directorio de salida para los CSV (default: directorio actual)"
    )
    args = parser.parse_args()

    match_id = args.match_id
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    print(f"Scrapeando partido {match_id} de FotMob...")

    # 1. Descargar y parsear
    json_data = fetch_match_html(match_id)
    content = extract_content(json_data)

    # 2. Info basica
    info = extract_match_info(content)
    print(f"\nPartido: {info['home_team']} {info['home_score']} - {info['away_score']} {info['away_team']}")

    # 3. Estadisticas del partido
    stats_df = extract_match_stats(content)
    if not stats_df.empty:
        path = os.path.join(output_dir, f"fotmob_{match_id}_stats.csv")
        stats_df.to_csv(path, index=False)
        print(f"  Estadisticas: {len(stats_df)} metricas -> {path}")
    else:
        print("  Estadisticas: no disponibles")

    # 4. Shotmap
    shots_df = extract_shotmap(content)
    if not shots_df.empty:
        path = os.path.join(output_dir, f"fotmob_{match_id}_shots.csv")
        shots_df.to_csv(path, index=False)
        print(f"  Shotmap: {len(shots_df)} tiros -> {path}")
    else:
        print("  Shotmap: no disponible (sin datos de coordenadas)")

    # 5. Alineaciones
    lineup_df = extract_lineups(content)
    if not lineup_df.empty:
        path = os.path.join(output_dir, f"fotmob_{match_id}_lineups.csv")
        lineup_df.to_csv(path, index=False)
        print(f"  Alineaciones: {len(lineup_df)} jugadores -> {path}")
    else:
        print("  Alineaciones: no disponibles")

    # 6. Eventos
    events_df = extract_events(content)
    if not events_df.empty:
        path = os.path.join(output_dir, f"fotmob_{match_id}_events.csv")
        events_df.to_csv(path, index=False)
        print(f"  Eventos: {len(events_df)} -> {path}")
    else:
        print("  Eventos: no disponibles")

    # 7. Estadisticas individuales
    player_df = extract_player_stats(content)
    if not player_df.empty:
        path = os.path.join(output_dir, f"fotmob_{match_id}_players.csv")
        player_df.to_csv(path, index=False)
        print(f"  Jugadores: {len(player_df)} -> {path}")
    else:
        print("  Estadisticas individuales: no disponibles")

    # 8. JSON crudo (para exploracion)
    raw_path = os.path.join(output_dir, f"fotmob_{match_id}_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    print(f"  JSON crudo: {raw_path}")

    print(f"\nExportacion completada en: {os.path.abspath(output_dir)}/")


if __name__ == "__main__":
    main()
