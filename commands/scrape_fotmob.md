# Comando: Scrape FotMob Match

Scraper reutilizable para extraer datos de partidos de FotMob y exportarlos en formato CSV compatible con las tareas del homework.

## Uso

```bash
# Uso basico — exporta CSVs en el directorio actual
python commands/scrape_fotmob.py <match_id>

# Exportar a un directorio especifico
python commands/scrape_fotmob.py <match_id> --output-dir data/fotmob

# Ejemplo con el partido Sport Boys vs Deportivo Garcilaso
python commands/scrape_fotmob.py 5169244 --output-dir data/fotmob
```

## Como obtener el match_id

1. Ir a [FotMob](https://www.fotmob.com) y buscar el partido
2. El `match_id` es el numero al final de la URL: `https://www.fotmob.com/matches/...#<match_id>`
3. Ejemplo: `https://www.fotmob.com/matches/sport-boys-vs-deportivo-garcilaso/5gmbhvfg#5169244` → `match_id = 5169244`

## Archivos exportados

| Archivo | Contenido |
|---------|-----------|
| `fotmob_<id>_stats.csv` | Estadisticas del partido (posesion, tiros, pases, defensa, duelos, disciplina) |
| `fotmob_<id>_shots.csv` | Shotmap con coordenadas (x, y), xG, jugador, resultado del tiro |
| `fotmob_<id>_lineups.csv` | Alineaciones con posicion, rating, minutos, coordenadas de layout |
| `fotmob_<id>_events.csv` | Eventos del partido (goles, tarjetas, sustituciones) |
| `fotmob_<id>_players.csv` | Estadisticas individuales por jugador |
| `fotmob_<id>_raw.json` | JSON crudo completo para exploracion libre |

## Compatibilidad con tareas del homework

| Tarea | Operacion | Compatible? | Notas |
|-------|-----------|-------------|-------|
| T1 | Mapa de tiros | **Parcial** | Requiere shotmap con coordenadas. Disponible en ligas grandes (Champions, La Liga, Premier). No disponible en ligas menores (Liga 1 Peru). |
| T2 | Red de pases | **No** | FotMob no proporciona datos evento-a-evento de pases individuales con coordenadas. |
| T3 | Mapa de calor | **No** | Requiere coordenadas de pases individuales. FotMob solo tiene agregados. |
| T4 | Radar de pizza | **Si** | Se puede construir con estadisticas individuales de jugadores. Necesita acumular datos de multiples partidos para calcular percentiles. |
| T5 | Radar comparativo | **Si** | Mismo enfoque que T4 — acumular stats de jugadores en multiples partidos. |
| T6 | Beeswarm | **Si** | Requiere una metrica por jugador en multiples partidos. Scraping de multiples match_ids para construir el dataset. |

## Limitaciones

### Datos no disponibles en FotMob (vs StatsBomb)

1. **Sin coordenadas de pases individuales:** FotMob no expone eventos de pase con (x, y) de origen y destino. Esto impide crear redes de pases (T2) y mapas de calor de pases peligrosos (T3).

2. **Shotmap vacio en ligas menores:** La Liga 1 de Peru y otras ligas sin tracking avanzado no tienen datos de coordenadas de tiros. Las ligas europeas principales si los tienen.

3. **Sin xG en ligas menores:** El modelo xG de FotMob no cubre todas las competiciones. Sin xG, el mapa de tiros pierde la codificacion de tamano de marcador.

4. **Sin datos de posesion por zona:** No hay breakdown espacial de posesion, solo el porcentaje global.

5. **Estadisticas de jugadores limitadas a un partido:** FotMob muestra stats por partido, no acumuladas por temporada. Para T4/T5/T6 necesitas scraping de multiples partidos.

### Diferencias de coordenadas

- **StatsBomb:** Sistema 120x80 yardas, orientacion estandarizada
- **FotMob shotmap:** Sistema 0-1 normalizado (porcentaje del campo), orientacion puede variar
- **FotMob lineup layout:** Coordenadas relativas para posicionamiento visual, no coordenadas de campo reales

### Rate limiting

FotMob puede bloquear IPs con demasiadas peticiones. Para scraping de multiples partidos:
- Agregar delays entre peticiones (`time.sleep(3)`)
- Rotar User-Agents (ya implementado)
- Considerar proxies si se necesita volumen alto

## Sugerencias

### Para replicar las tareas del homework con FotMob

1. **T1 (Mapa de tiros):** Usar un partido de liga grande (Champions League, La Liga, Premier League) donde el shotmap tiene coordenadas y xG. Convertir coordenadas normalizadas (0-1) al sistema de `mplsoccer` (120x80).

2. **T2 (Red de pases):** No es posible con FotMob. Alternativa: usar las coordenadas de layout de la alineacion para visualizar la formacion del equipo con las posiciones y ratings como un "mapa de equipo" en lugar de red de pases.

3. **T3 (Mapa de calor):** No es posible con FotMob para pases. Alternativa: si hay shotmap con coordenadas, crear un mapa de calor de origenes de tiro en lugar de pases peligrosos.

4. **T4/T5/T6 (Radares y beeswarm):** Scrape multiples partidos de una temporada completa para acumular estadisticas por jugador. Luego calcular per90 y percentiles como en el homework.

### Flujo recomendado para ligas menores (sin shotmap/xG)

```
FotMob (Liga 1 Peru)
  -> stats.csv     -> Visualizacion de estadisticas de equipo (barras, radar de equipo)
  -> lineups.csv   -> Visualizacion de formacion con ratings
  -> events.csv    -> Timeline de eventos del partido
  -> players.csv   -> Comparacion de jugadores en un partido (radar simple)
```

### Combinacion FotMob + StatsBomb

Para maximizar la cobertura, usa StatsBomb para las tareas que requieren datos evento-a-evento (T1, T2, T3) y FotMob para complementar con datos de ligas/partidos que StatsBomb no cubre.

## Dependencias

```bash
pip install requests_html fake-useragent pandas
```
