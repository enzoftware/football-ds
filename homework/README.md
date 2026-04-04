# Proyecto Final — Data Science Aplicado al Futbol

## Descripcion

Este proyecto final recopila 6 ejercicios practicos de visualizacion y analisis de datos futbolisticos utilizando Python, siguiendo las tecnicas aprendidas durante el curso. Cada tarea se implementa en un notebook independiente con codigo documentado en espanol y un analisis escrito del resultado.

## Estructura de archivos

| Archivo | Tarea | Descripcion |
|---|---|---|
| `tarea1_mapa_tiros.ipynb` | Tarea 1 | Mapa de tiros del Atletico de Madrid (local) vs Barcelona (1-0) |
| `tarea2_red_pases.ipynb` | Tarea 2 | Red de pases del Atletico de Madrid (mismo partido) |
| `tarea3_mapa_calor.ipynb` | Tarea 3 | Mapa de calor de pases peligrosos (Real Madrid, La Liga 2015/16) |
| `tarea4_pizza_radar.ipynb` | Tarea 4 | Radar de pizza — Thomas Partey (Arsenal, mediocampista) |
| `tarea5_radar_comparativo.ipynb` | Tarea 5 | Radar clasico comparativo — Bruno Fernandes vs Alexis Mac Allister |
| `tarea6_beeswarm.ipynb` | Tarea 6 | Grafico beeswarm — Mateo Kovacic y Granit Xhaka |

## Datos utilizados

### StatsBomb Open Data (Tareas 1, 2, 3)
- **Partido (T1, T2):** Atletico de Madrid 1-0 Barcelona — La Liga 2020/2021, 21 de noviembre de 2020 (`match_id=3773656`)
- **Competicion (T3):** La Liga 2015/2016 (`competition_id=11`, `season_id=27`) — 38 partidos del Real Madrid
- **Fuente:** [StatsBomb Open Data](https://github.com/statsbomb/open-data) via `statsbombpy` y `statsbomb`

### FBref / CSV del curso (Tareas 4, 5, 6)
- `data/pizza_tutorial9.csv` — Estadisticas defensivas de jugadores de la Premier League 2020/21
- `data/radars10.csv` — Estadisticas de tiro de jugadores de la Premier League 2020/21
- `data/beeswarmTutorial11.csv` — Pases progresivos de jugadores de la Premier League 2020/21

## Elecciones realizadas

### Partido (Tareas 1 y 2)
Se eligio **Atletico de Madrid 1-0 Barcelona** de La Liga 2020/21. Este partido es interesante porque refleja el estilo defensivo y de contragolpe clasico del equipo de Simeone, con el gol solitario de Yannick Carrasco en transicion.

### Equipo (Tarea 3)
Se analizo al **Real Madrid** en La Liga 2015/16 (38 partidos completos). Se eligio esta temporada porque es la unica en los datos abiertos de StatsBomb que contiene todos los partidos del Real Madrid, permitiendo un mapa de calor representativo de toda la temporada.

### Jugador individual (Tarea 4)
Se eligio a **Thomas Partey** (Arsenal, mediocampista) en lugar de un defensor como en el temario. Partey, fichaje estrella del Arsenal procedente del Atletico de Madrid, ofrece un perfil defensivo amplio ideal para este tipo de radar.

### Comparacion radar (Tarea 5)
Se compararon **Bruno Fernandes** (Manchester United) y **Alexis Mac Allister** (Brighton), dos mediocampistas creativos/ofensivos. Se usaron `drop` para eliminar las metricas de delanteros (FK, PK, PKatt, SoT%, G/Sh, G/SoT) que no son relevantes para mediocampistas.

### Beeswarm (Tarea 6)
Se destacaron **Mateo Kovacic** (Chelsea) y **Granit Xhaka** (Arsenal), ambos mediocampistas puros (MF) del top 6 de la Premier League 2020/21 en pases progresivos per90. Ambos comparten posicion y nivel estadistico similar (~8.0 per90) pero con estilos de juego diferentes.

## Librerias necesarias

```bash
pip install statsbombpy statsbomb mplsoccer soccerplots pandas numpy scipy matplotlib seaborn highlight_text
```

## Como ejecutar

1. Abrir cada notebook en Jupyter Notebook o JupyterLab
2. Ejecutar todas las celdas en orden (Kernel > Restart & Run All)
3. Los graficos se generan inline en el notebook
4. La tarea 4 exporta adicionalmente el radar como `pizza_partey.png`

## Nota sobre Tarea 7

La tarea 7 requiere el uso de **Tableau** para crear dos graficos personalizados con cualquier CSV del curso. Al ser una herramienta grafica externa, no se incluye en este repositorio de notebooks. Los graficos de Tableau deben realizarse por separado y exportarse como imagenes o PDF para incluir en la entrega final.
