# Football Data Science

A progressive collection of Jupyter notebooks covering football (soccer) data analysis and visualization, from web scraping and event data exploration to advanced player profiling and tactical charts. Each notebook is self-contained and builds on techniques introduced in previous ones.

---

## Project Structure

```
football-ds/
├── data/                          # All CSV datasets used by the notebooks
│   ├── messibetis6.csv            # Messi pass events vs Real Betis
│   ├── convextutorial7.csv        # Player action coordinates (team 65)
│   ├── xgtutorial8.csv            # Shot-level xG data (Southampton vs Bournemouth)
│   ├── pizza_tutorial9.csv        # FBref PL defender stats 2020-21
│   ├── radars10.csv               # FBref PL full player stats 2020-21
│   └── beeswarmTutorial11.csv     # FBref PL progressive pass data 2020-21
├── 1_scraping_fotmob.ipynb
├── 2_statsbomb_scrapping.ipynb
├── 3_shoots_map.ipynb
├── 4_pass_network.ipynb
├── 5_players_heatmap.ipynb
├── 6_individual_player_heatmap.ipynb
├── 7_action_radios.ipynb
├── 8_xg_match_phases.ipynb
├── 9_pizza_radar.ipynb
├── 10_comparative_radar.ipynb
└── 11_beeswarm_comparative.ipynb
```

---

## Notebooks

### 1 — FotMob Match Statistics Scraper
**File:** `1_scraping_fotmob.ipynb`

Extracts structured match statistics from FotMob without using any official API. FotMob is built on Next.js, which embeds its full server-side rendered state in a `<script id="__NEXT_DATA__">` tag. A regex pattern captures this JSON blob, which is then traversed to extract match stats (xG, shots, passes, physical metrics, duels, discipline) and a full shot map per team.

**Key techniques:** `requests_html`, `fake_useragent` for bot-detection mitigation, `re.search` with `DOTALL` for `__NEXT_DATA__` extraction, nested JSON traversal, `pd.json_normalize`.

---

### 2 — StatsBomb Open Data Exploration
**File:** `2_statsbomb_scrapping.ipynb`

Introduces the StatsBomb Open Data API via `statsbombpy`. Covers the three-level discovery hierarchy (competitions → matches → events), the wide-format event model, and the StatsBomb 120×80 pitch coordinate system. Demonstrates how to reduce the 80+ column event DataFrame to a working subset for further analysis.

**Key techniques:** `sb.competitions()`, `sb.matches()`, `sb.events()`, column projection, StatsBomb event taxonomy.

---

### 3 — Shot Map with xG Encoding
**File:** `3_shoots_map.ipynb`

Constructs a progressive shot map visualization using StatsBomb event data and `mplsoccer`. Progresses from an empty half-pitch to a team-filtered, xG-weighted scatter plot. Demonstrates the `VerticalPitch(half=True)` layout and xG-as-marker-size encoding (`s = xg * 500 + 100`).

**Key techniques:** `statsbomb.Events`, `get_dataframe(event_type='shot')`, `VerticalPitch`, `pitch.scatter`, xG size encoding.

---

### 4 — Pass Network Analysis
**File:** `4_pass_network.ipynb`

Builds a pass network graph for Côte d'Ivoire using `mplsoccer`'s `Sbopen` parser. Players are represented as nodes (positioned at their average touch location) and pass pairs as weighted edges (line width ∝ pass volume). Includes pre-substitution filtering and canonical pair-key construction via alphabetical name sorting.

**Key techniques:** `Sbopen().event()`, successful-pass filter (`outcome_name.isnull()`), centroid position computation with `np.concatenate` + `np.mean`, `groupby` edge aggregation, `pitch.lines`.

---

### 5 — Danger Pass Heatmap
**File:** `5_players_heatmap.ipynb`

Identifies "danger passes" — completed passes occurring within a 15-second window before a shot — and visualizes their spatial distribution across all of Spain's Euro 2020 matches. Produces both a raw scatter and a normalized per-match binned heatmap.

**Key techniques:** `parser.match()`, time-window danger pass detection (minute×60+second arithmetic), period-boundary clamping, `pitch.bin_statistic`, `pitch.heatmap`, per-match normalization.

---

### 6 — Individual Player Pass Map with KDE
**File:** `6_individual_player_heatmap.ipynb`

Visualizes Messi's second-half passing in a specific match with outcome-coded pass lines (yellow = successful, red = unsuccessful) overlaid with a 2D kernel density estimate showing his dominant zones of activity. Uses a custom CSV with raw coordinates rescaled to the StatsBomb 120×80 system.

**Key techniques:** Coordinate rescaling (`x*1.2`, `y*0.8`), `plt.plot` for pass trajectories, `plt.gca().invert_yaxis()`, `sns.kdeplot` with `fill=True`, layered visualization with alpha blending.

---

### 7 — Player Action Radius via Convex Hull
**File:** `7_action_radios.ipynb`

Computes and visualizes the spatial "action radius" of a specific player using `scipy.spatial.ConvexHull` — the minimal convex polygon enclosing all of their action coordinates. Z-score outlier removal is applied before hull computation to prevent tracking errors from distorting the boundary.

**Key techniques:** `ConvexHull`, z-score outlier filtering (`scipy.stats.zscore`, 3σ threshold), `hull.simplices` edge rendering, `plt.fill` for polygon shading, `hull.volume` as spatial coverage metric.

---

### 8 — xG Match Timeline
**File:** `8_xg_match_phases.ipynb`

Builds two complementary xG visualizations for a Southampton vs Bournemouth match. The cumulative step chart (`ax.step(where='post')`) shows the xG narrative across 90 minutes. A supplementary diverging shot timeline (added as a separate cell) plots each individual shot as a vertical stem — height = xG, direction = team — with goal shots marked by a star.

**Key techniques:** Cumulative sum via manual running total, `ax.step(where='post')`, diverging stem chart, `solid_capstyle='round'`, `matplotlib.lines.Line2D` for custom legend handles.

---

### 9 — Pizza Radar Chart (Single Player Percentile Profile)
**File:** `9_pizza_radar.ipynb`

Generates a pizza/donut-style radar chart for Trent Alexander-Arnold, displaying his percentile rank across 14 defensive metrics compared to all Premier League defenders in 2020-21 with at least 15 full 90s played. Each slice height represents a percentile score (0–99).

**Key techniques:** FBref name cleaning (`str.split('\\')`), playing-time threshold filtering, `scipy.stats.percentileofscore`, `math.floor`, 99-percentile cap for PyPizza, `mplsoccer.PyPizza`, `plt.savefig(dpi=500)`.

---

### 10 — Comparative Radar Chart (Dual Player)
**File:** `10_comparative_radar.ipynb`

Renders a comparative radar with two overlapping filled polygons (Tammy Abraham vs Harry Kane) across 14 attacking metrics using `soccerplots`. Unlike the pizza chart, this radar uses raw absolute values scaled to per-axis ranges, enabling direct head-to-head comparison.

**Key techniques:** `soccerplots.radar_chart.Radar`, per-axis range construction with 25% padding, `compare=True` dual-polygon mode, `alphas` for transparency layering.

---

### 11 — Beeswarm Plot (Progressive Pass Distribution)
**File:** `11_beeswarm_comparative.ipynb`

Produces a beeswarm distribution chart of progressive passes per 90 minutes across all outfield Premier League players in 2020-21 (minimum 6.5 90s played). Thiago Alcântara and Kevin De Bruyne are highlighted as reference points against the full population distribution.

**Key techniques:** `sns.swarmplot`, per-90 normalization, playing-time threshold, goalkeeper exclusion, `zorder`-based point overlay for player highlighting.

---

## Setup

```bash
pip install pandas numpy matplotlib seaborn scipy mplsoccer statsbombpy soccerplots highlight_text requests_html fake-useragent
```

All CSV datasets are stored in the `data/` directory. Notebooks that use StatsBomb Open Data fetch it directly via the library — no credentials or local files required for those.

---

## Data Sources

- **StatsBomb Open Data** — Free event-level match data for selected competitions: https://github.com/statsbomb/open-data
- **FBref** — Season-level aggregated player stats exported as CSV: https://fbref.com
- **FotMob** — Live and historical match stats (scraped via `__NEXT_DATA__`): https://www.fotmob.com

---

## Reference Reading

### Football Analytics Fundamentals
- *Soccermatics* — David Sumpter. Mathematical models applied to football tactics and data.
- *The Expected Goals Philosophy* — James Tippett. Accessible introduction to the xG model and its applications.
- StatsBomb blog — Technical articles on event data methodology, xG models, and pressing metrics: https://statsbomb.com/articles/

### Python Libraries
- **mplsoccer documentation**: https://mplsoccer.readthedocs.io
- **statsbombpy documentation**: https://github.com/statsbomb/statsbombpy
- **soccerplots documentation**: https://github.com/Slothfulwave612/soccerplots
- **seaborn documentation** (swarmplot, kdeplot): https://seaborn.pydata.org

### Key Metrics and Concepts
- **xG (Expected Goals)** — StatsBomb xG model methodology: https://statsbomb.com/articles/soccer/statsbomb-xg-methodology/
- **Progressive passes** — FBref metric glossary: https://fbref.com/en/about/glossary
- **PPDA (Passes Per Defensive Action)** — Pressing intensity metric explanation: https://www.statsperform.com/resource/introducing-new-passing-metrics/
- **Pass networks in football** — Academic overview: https://www.sciencedirect.com/science/article/pii/S1877705817302461
- **Convex hull for spatial coverage** — Applied to player analysis: https://www.analyticsvidhya.com/blog/2021/11/convex-hull-in-python/

### Visualization References
- **The Visual Display of Quantitative Information** — Edward Tufte. Canonical reference for data visualization design principles.
- **Football Slices (pizza charts)** — Andy Watson's tutorials on mplsoccer PyPizza: https://mplsoccer.readthedocs.io/en/latest/gallery/pizza_plots/
- **Beeswarm plots for sports data** — Observable HQ examples: https://observablehq.com/@d3/beeswarm
