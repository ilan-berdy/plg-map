# PLG Scribe Engagement — County Choropleth

Interactive county-level heat map of PLG user engagement (Scribe creation & events).

**[▶ View Live Map](./index.html)** ← works once hosted on GitHub Pages, Netlify, or any static host

![Preview](https://img.shields.io/badge/counties-1%2C675-38bdf8) ![Preview](https://img.shields.io/badge/coverage-95.1%25-34d399)

## Quick Start

### Option A: Just view/share the HTML
Open `index.html` in any browser. No install needed.

### Option B: Regenerate from fresh data
```bash
pip install plotly pandas zipcodes addfips kaleido

# Interactive HTML (opens in browser)
python generate.py

# Filter to one state
python generate.py --state "Texas"

# Export static PNGs
python generate.py --export all

# Export single state as PNG
python generate.py --state "California" --export png

# Use linear scale instead of log
python generate.py --linear
```

## Git & GitHub

This project is set up for Git. To connect to GitHub and push:

```bash
# Create a new repo on GitHub (github.com → New repository), then:
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

**Typical workflow:**
```bash
git add .
git commit -m "Describe your changes"
git push
```

**Clone the project elsewhere:**
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

## Hosting (to get a shareable link)

### GitHub Pages (recommended)
1. Push this repo to GitHub (see **Git & GitHub** above).
2. In the repo: **Settings → Pages → Source** → choose **Deploy from a branch**.
3. Branch: **main**, folder: **/ (root)**. Save.
4. Share the URL: `https://<your-username>.github.io/<repo-name>/`

### Netlify (fastest, no account needed)
1. Go to [app.netlify.com/drop](https://app.netlify.com/drop)
2. Drag the entire project folder
3. Get an instant shareable link

### Vercel
```bash
npx vercel --prod
```

## Project Structure
```
├── index.html          # Interactive map (loads data/plg_data.js when present)
├── generate.py         # Python script to regenerate from new data
├── data/
│   ├── PLG_User_Count_Insights.csv
│   ├── plg_data.js     # Optional: built by scripts/build_plg_data.py (supports EHR)
│   └── facility_by_state.js
├── scripts/
│   ├── build_plg_data.py   # Build plg_data.js from geocoded CSV (optional EHR column)
│   └── build_facility_data.py
└── README.md
```

## Features
- **State dropdown** — filter to any US state with auto-zoom
- **Metric toggle** — Uniques, Events, or side-by-side comparison
- **Log/Linear scale** — toggle to handle skewed distributions
- **Export PNG** — button in the toolbar downloads current view as hi-res image
- **KPI summary** — auto-updating totals and top counties
- **Facility paragraph** — optional; when enabled and a state is selected, the sidebar shows large health systems and smaller provider organizations (from `data/facility_by_state.js`). Off by default; set `SHOW_FACILITY_PARAGRAPH = true` in `index.html` to show it.
- **EHR data** — county hover and state sidebar can show top EHRs when data is built from a CSV that includes an EHR column (e.g. `c. EHR`). See **Building plg_data.js** below.

## How It Works
1. Cities from the CSV are mapped to US counties via the `zipcodes` Python package (95.1% match rate)
2. Data is aggregated at the county FIPS level
3. Plotly.js renders the choropleth using Census Bureau county boundaries
4. The HTML is fully self-contained — data is embedded, GeoJSON loads from Plotly's CDN

## Updating with New Data
1. Replace `data/PLG_User_Count_Insights.csv` with your new export, or use a **geocoded CSV** that includes **State FIPS** and **County FIPS** columns (e.g. from Geocodio). The script auto-detects this format and aggregates by FIPS directly—no zipcodes/addfips needed.
2. Update the `CSV_PATH` in `generate.py` if the filename changed, or pass `--csv "path/to/your.csv"`.
3. Run `python generate.py --export html` (or `python generate.py --csv "plg_data - raw_data.csv"` for a geocoded file).
4. Copy the generated `choropleth_exports/plg_choropleth_interactive.html` to `index.html` if that’s your main app, then commit and push.

### Building plg_data.js from a raw CSV (with optional EHR)
To use a geocoded CSV that includes an EHR column (e.g. `c. EHR`), build the app data and optional state summaries:

```bash
# One-time: create venv and install pandas (if your system Python is externally managed)
python3 -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install pandas

python scripts/build_plg_data.py "path/to/plg_data - raw_data (1).csv"
```

If pandas is already installed (e.g. in your existing env), you can run the script directly.

This writes `data/plg_data.js` with `ALL_DATA`, `STATES`, and `SUMMARIES` (including top EHRs per state). The app loads this file when present and falls back to embedded data otherwise.

### Updating the facility paragraph (large/small organizations per state)
The state view sidebar includes a paragraph listing large health systems (e.g. HCA, CHS, Ochsner) and smaller provider organizations. To refresh this from your CSVs:

```bash
python scripts/build_facility_data.py \
  --large "/path/to/plg_data - large_facilities.csv" \
  --small "/path/to/plg_data - small_facilities.csv" > data/facility_by_state.js
```

Then reload the app; the sidebar will use the new `data/facility_by_state.js`.

## Data Coverage
- **4,576 / 4,811** cities matched to counties (95.1%)
- **1,675** unique counties with data
- Common misses: very small towns, "undefined" entries, hyphenated/alternate city names
