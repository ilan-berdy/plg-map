"""
PLG Scribe Engagement - County-Level Choropleth Heat Map
=========================================================
Generates interactive county choropleth maps from PLG user data.

Usage:
    python plg_county_choropleth.py                    # Opens interactive HTML in browser
    python plg_county_choropleth.py --state "Texas"     # Filter to a single state
    python plg_county_choropleth.py --export png        # Export as PNG
    python plg_county_choropleth.py --export pdf        # Export as PDF
    python plg_county_choropleth.py --export all        # Export both metrics as separate PNGs + combined HTML

Requirements:
    pip install plotly pandas zipcodes addfips kaleido
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import zipcodes
import addfips
import numpy as np
import json
import argparse
import os
import sys
from collections import Counter
from urllib.request import urlopen

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
CSV_PATH = "data/PLG_User_Count_Insights.csv"
OUTPUT_DIR = "choropleth_exports"
GEOJSON_URL = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"

STATE_ABBREVS = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI',
    'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME',
    'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
    'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE',
    'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
    'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI',
    'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
    'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# State center coordinates for zoom when filtering
STATE_CENTERS = {
    'AL': (32.8, -86.8), 'AK': (64.0, -153.0), 'AZ': (34.3, -111.7),
    'AR': (34.8, -92.2), 'CA': (37.2, -119.5), 'CO': (39.0, -105.5),
    'CT': (41.6, -72.7), 'DE': (39.0, -75.5), 'DC': (38.9, -77.0),
    'FL': (28.6, -82.4), 'GA': (32.7, -83.5), 'HI': (20.5, -157.4),
    'ID': (44.4, -114.6), 'IL': (40.0, -89.2), 'IN': (39.8, -86.3),
    'IA': (42.0, -93.5), 'KS': (38.5, -98.3), 'KY': (37.8, -85.7),
    'LA': (31.0, -92.0), 'ME': (45.4, -69.2), 'MD': (39.0, -76.8),
    'MA': (42.3, -71.8), 'MI': (44.3, -85.4), 'MN': (46.3, -94.3),
    'MS': (32.7, -89.7), 'MO': (38.4, -92.5), 'MT': (47.0, -109.6),
    'NE': (41.5, -99.8), 'NV': (39.3, -116.6), 'NH': (43.7, -71.6),
    'NJ': (40.1, -74.7), 'NM': (34.4, -106.1), 'NY': (42.9, -75.5),
    'NC': (35.5, -79.8), 'ND': (47.4, -100.4), 'OH': (40.4, -82.8),
    'OK': (35.6, -97.5), 'OR': (44.0, -120.5), 'PA': (40.9, -77.8),
    'RI': (41.7, -71.5), 'SC': (33.9, -80.9), 'SD': (44.4, -100.2),
    'TN': (35.9, -86.4), 'TX': (31.5, -99.4), 'UT': (39.3, -111.7),
    'VT': (44.1, -72.6), 'VA': (37.5, -78.9), 'WA': (47.4, -120.5),
    'WV': (38.6, -80.6), 'WI': (44.6, -89.8), 'WY': (43.0, -107.6),
}


# ---------------------------------------------------------------------------
# STEP 1: Load & clean data
# ---------------------------------------------------------------------------
def is_geocoded_csv(csv_path):
    """Check if CSV has Geocodio FIPS columns (State FIPS, County FIPS)."""
    try:
        df = pd.read_csv(csv_path, nrows=1)
        df.columns = df.columns.str.strip()
        return 'State FIPS' in df.columns and 'County FIPS' in df.columns
    except Exception:
        return False


def load_and_aggregate_geocoded(csv_path):
    """
    Load geocoded CSV (with State FIPS + County FIPS) and aggregate to county level.
    Returns same structure as aggregate_by_county() for compatibility.
    """
    print(f"Loading geocoded data from {csv_path}...")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df = df[~df['Region'].isin(['undefined', 'Region'])].copy()
    df['state_abbr'] = df['Region'].map(STATE_ABBREVS)
    df = df.dropna(subset=['state_abbr'])

    # Build 5-digit FIPS: State FIPS (2) + County FIPS (3)
    df['State FIPS'] = pd.to_numeric(df['State FIPS'], errors='coerce')
    df['County FIPS'] = pd.to_numeric(df['County FIPS'], errors='coerce')
    df = df.dropna(subset=['State FIPS', 'County FIPS'])
    state_str = df['State FIPS'].astype(int).astype(str).str.zfill(2)
    county_str = df['County FIPS'].astype(int).astype(str)
    # County FIPS may be 3+ digits; keep last 3 for 5-digit FIPS
    county_str = county_str.str[-3:].str.zfill(3)
    df['fips'] = state_str + county_str

    df['A. Uniques of First Scribe Created'] = pd.to_numeric(
        df['A. Uniques of First Scribe Created'], errors='coerce'
    ).fillna(0).astype(int)
    df['B. Total Events of Scribe Created'] = pd.to_numeric(
        df['B. Total Events of Scribe Created'], errors='coerce'
    ).fillna(0).astype(int)

    # County name: use Geocodio County if present, else derive from FIPS later
    county_name_col = 'Geocodio County' if 'Geocodio County' in df.columns else None
    if county_name_col:
        df['county_name'] = df[county_name_col].fillna('').astype(str)
    else:
        df['county_name'] = ''

    county_df = (
        df.groupby(['fips', 'county_name', 'Region', 'state_abbr'])
        .agg({
            'A. Uniques of First Scribe Created': 'sum',
            'B. Total Events of Scribe Created': 'sum',
            'City': 'count'
        })
        .reset_index()
        .rename(columns={'City': 'num_cities'})
    )
    county_df['fips'] = county_df['fips'].astype(str).str.zfill(5)
    # If county_name is empty (no Geocodio County column), use a placeholder
    county_df['county_name'] = county_df.apply(
        lambda r: r['county_name'] if r['county_name'] else f"County {r['fips'][2:]}",
        axis=1
    )
    print(f"  Loaded {len(df)} rows → {len(county_df)} counties (geocoded FIPS)")
    return county_df


def load_data(csv_path):
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df = df[~df['Region'].isin(['undefined', 'Region'])].copy()
    df['state_abbr'] = df['Region'].map(STATE_ABBREVS)
    df = df.dropna(subset=['state_abbr'])
    df['A. Uniques of First Scribe Created'] = pd.to_numeric(
        df['A. Uniques of First Scribe Created'], errors='coerce'
    ).fillna(0).astype(int)
    df['B. Total Events of Scribe Created'] = pd.to_numeric(
        df['B. Total Events of Scribe Created'], errors='coerce'
    ).fillna(0).astype(int)
    print(f"  Loaded {len(df)} rows across {df['Region'].nunique()} states")
    return df


# ---------------------------------------------------------------------------
# STEP 2: Map cities → counties using the zipcodes package
# ---------------------------------------------------------------------------
def map_cities_to_counties(df):
    print("Mapping cities to counties...")
    def get_county(city, state_abbr):
        try:
            results = zipcodes.filter_by(city=city, state=state_abbr)
            if results:
                counties = [r['county'] for r in results if r.get('county')]
                if counties:
                    return Counter(counties).most_common(1)[0][0]
        except Exception:
            pass
        return None

    df['county_name'] = df.apply(
        lambda r: get_county(r['City'], r['state_abbr']), axis=1
    )
    matched = df['county_name'].notna().sum()
    print(f"  Matched {matched}/{len(df)} cities ({matched/len(df)*100:.1f}%)")

    # Get FIPS codes
    af = addfips.AddFIPS()
    def get_fips(county_name, state_name):
        if pd.isna(county_name):
            return None
        clean = county_name
        for suffix in [' County', ' Parish', ' Borough', ' Census Area',
                       ' Municipality', ' Municipio', ' city']:
            clean = clean.replace(suffix, '')
        try:
            return af.get_county_fips(clean.strip(), state=state_name)
        except Exception:
            return None

    df['fips'] = df.apply(lambda r: get_fips(r['county_name'], r['Region']), axis=1)
    fips_ok = df['fips'].notna().sum()
    print(f"  FIPS resolved for {fips_ok}/{len(df)} cities ({fips_ok/len(df)*100:.1f}%)")
    return df


# ---------------------------------------------------------------------------
# STEP 3: Aggregate to county level
# ---------------------------------------------------------------------------
def aggregate_by_county(df):
    county_df = (
        df[df['fips'].notna()]
        .groupby(['fips', 'county_name', 'Region', 'state_abbr'])
        .agg({
            'A. Uniques of First Scribe Created': 'sum',
            'B. Total Events of Scribe Created': 'sum',
            'City': 'count'
        })
        .reset_index()
        .rename(columns={'City': 'num_cities'})
    )
    county_df['fips'] = county_df['fips'].astype(str).str.zfill(5)
    print(f"  Aggregated to {len(county_df)} counties")
    return county_df


# ---------------------------------------------------------------------------
# STEP 4: Load county GeoJSON
# ---------------------------------------------------------------------------
def load_geojson():
    """
    Fetch county GeoJSON. Tries local cache first, then downloads.
    Returns None if unavailable (HTML export still works via client-side fetch).
    """
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'geojson-counties-fips.json')
    if os.path.exists(cache_path):
        print(f"Loading county GeoJSON from cache: {cache_path}")
        with open(cache_path) as f:
            geojson = json.load(f)
        print(f"  Loaded {len(geojson['features'])} county boundaries")
        return geojson
    try:
        print("Fetching county GeoJSON from Plotly datasets...")
        with urlopen(GEOJSON_URL) as response:
            data = response.read()
            geojson = json.loads(data)
        # Cache for next time
        with open(cache_path, 'wb') as f:
            f.write(data)
        print(f"  Loaded {len(geojson['features'])} county boundaries (cached to {cache_path})")
        return geojson
    except Exception as e:
        print(f"  ⚠ Could not fetch GeoJSON: {e}")
        print("    → Interactive HTML will load it client-side in the browser.")
        print("    → For static PNG/PDF export, first download the file manually:")
        print(f"      curl -o {cache_path} {GEOJSON_URL}")
        return None


# ---------------------------------------------------------------------------
# STEP 5: Build choropleth figure
# ---------------------------------------------------------------------------
def build_figure(county_df, geojson, state_filter=None, use_log=True):
    """
    Build a side-by-side choropleth with Uniques (left) and Events (right).
    Optionally filter to a single state.
    """
    data = county_df.copy()
    title_suffix = ""
    geo_scope = "usa"

    if state_filter:
        abbr = STATE_ABBREVS.get(state_filter, state_filter)
        # Accept either full name or abbreviation
        if len(state_filter) == 2:
            abbr = state_filter.upper()
            state_filter = {v: k for k, v in STATE_ABBREVS.items()}.get(abbr, state_filter)
        data = data[data['state_abbr'] == abbr]
        title_suffix = f" — {state_filter}"

        if len(data) == 0:
            print(f"  ⚠ No data for state: {state_filter}")
            return None

        # Filter geojson to only this state's FIPS (first 2 digits = state FIPS)
        state_fips_prefix = data['fips'].iloc[0][:2]
        filtered_features = [
            f for f in geojson['features']
            if str(f.get('id', '')).startswith(state_fips_prefix)
        ]
        filtered_geojson = {**geojson, 'features': filtered_features}
    else:
        filtered_geojson = geojson

    # Hover text
    data['hover'] = (
        data['county_name'] + ', ' + data['Region']
        + '<br>Uniques: ' + data['A. Uniques of First Scribe Created'].astype(str)
        + '<br>Total Events: ' + data['B. Total Events of Scribe Created'].apply(lambda x: f'{x:,}')
        + '<br>Cities: ' + data['num_cities'].astype(str)
    )

    # Color values
    if use_log:
        data['z_uniques'] = np.log1p(data['A. Uniques of First Scribe Created'])
        data['z_events'] = np.log1p(data['B. Total Events of Scribe Created'])
    else:
        data['z_uniques'] = data['A. Uniques of First Scribe Created']
        data['z_events'] = data['B. Total Events of Scribe Created']

    # --- Build subplots ---
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            '<b>Unique First Scribes Created</b>',
            '<b>Total Scribe Events</b>'
        ],
        specs=[[{"type": "choropleth"}, {"type": "choropleth"}]],
        horizontal_spacing=0.03,
    )

    blue_scale = [
        [0, '#0d1b2a'], [0.15, '#0e3b5e'], [0.35, '#146b8e'],
        [0.55, '#1a9ec2'], [0.75, '#38bdf8'], [1, '#bae6fd']
    ]
    purple_scale = [
        [0, '#0d0a1a'], [0.15, '#261454'], [0.35, '#4a2592'],
        [0.55, '#7044d4'], [0.75, '#a78bfa'], [1, '#ddd6fe']
    ]

    def make_colorbar(metric, position):
        vals = data[f'A. Uniques of First Scribe Created' if metric == 'u' else 'B. Total Events of Scribe Created']
        label = 'Uniques' if metric == 'u' else 'Events'
        cb = dict(
            title=dict(text=label, font=dict(size=12)),
            len=0.55, thickness=14, x=position,
            tickfont=dict(size=10),
        )
        if use_log:
            max_val = vals.max()
            ticks = [v for v in [0, 1, 5, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000] if v <= max_val * 1.2]
            cb['tickvals'] = [np.log1p(v) for v in ticks]
            cb['ticktext'] = [f'{v:,}' if v < 1000 else f'{v//1000}k' for v in ticks]
        return cb

    # Uniques map (left)
    fig.add_trace(go.Choropleth(
        geojson=filtered_geojson,
        locations=data['fips'],
        z=data['z_uniques'],
        text=data['hover'],
        hoverinfo='text',
        colorscale=blue_scale,
        colorbar=make_colorbar('u', 0.44),
        marker_line=dict(width=0.3, color='#1e2a3a'),
        hoverlabel=dict(bgcolor='#121825', bordercolor='#1e2a3a',
                        font=dict(size=12, color='#e2e8f0')),
    ), row=1, col=1)

    # Events map (right)
    fig.add_trace(go.Choropleth(
        geojson=filtered_geojson,
        locations=data['fips'],
        z=data['z_events'],
        text=data['hover'],
        hoverinfo='text',
        colorscale=purple_scale,
        colorbar=make_colorbar('e', 1.01),
        marker_line=dict(width=0.3, color='#1e2a3a'),
        hoverlabel=dict(bgcolor='#121825', bordercolor='#1e2a3a',
                        font=dict(size=12, color='#e2e8f0')),
    ), row=1, col=2)

    # Geo settings
    geo_common = dict(
        bgcolor='rgba(0,0,0,0)',
        lakecolor='#0a0e17',
        landcolor='#0f1520',
        showlakes=True,
        showland=True,
        subunitcolor='#1e2a3a',
    )

    if state_filter and abbr in STATE_CENTERS:
        lat, lon = STATE_CENTERS[abbr]
        geo_common.update(
            projection=dict(type='albers usa'),
            center=dict(lat=lat, lon=lon),
        )
        fig.update_geos(scope='usa', fitbounds='locations', visible=False, **geo_common)
    else:
        fig.update_geos(scope='usa', projection_type='albers usa', **geo_common)

    # Layout
    scale_label = "Log Scale" if use_log else "Linear Scale"
    fig.update_layout(
        title=dict(
            text=f'PLG Scribe Engagement by County{title_suffix}<br>'
                 f'<span style="font-size:13px;color:#8492a6">'
                 f'Feb 14 2025 → Feb 9 2026 · {len(data)} counties · {scale_label}</span>',
            font=dict(size=20, color='#e2e8f0'),
            x=0.5, xanchor='center',
        ),
        paper_bgcolor='#0a0e17',
        plot_bgcolor='#0a0e17',
        font=dict(color='#e2e8f0'),
        margin=dict(t=90, b=20, l=20, r=20),
        height=600,
        width=1400,
    )

    # Style subtitle font
    for ann in fig.layout.annotations:
        ann.font = dict(size=14, color='#8492a6')

    return fig


def build_single_figure(county_df, geojson, metric='events', state_filter=None, use_log=True):
    """
    Build a single-metric choropleth (for individual exports).
    metric: 'uniques' or 'events'
    """
    data = county_df.copy()
    title_suffix = ""
    abbr = None

    if state_filter:
        abbr = STATE_ABBREVS.get(state_filter, state_filter)
        if len(state_filter) == 2:
            abbr = state_filter.upper()
            state_filter = {v: k for k, v in STATE_ABBREVS.items()}.get(abbr, state_filter)
        data = data[data['state_abbr'] == abbr]
        title_suffix = f" — {state_filter}"
        if len(data) == 0:
            return None

        state_fips_prefix = data['fips'].iloc[0][:2]
        filtered_features = [
            f for f in geojson['features']
            if str(f.get('id', '')).startswith(state_fips_prefix)
        ]
        filtered_geojson = {**geojson, 'features': filtered_features}
    else:
        filtered_geojson = geojson

    is_uniques = metric == 'uniques'
    col = 'A. Uniques of First Scribe Created' if is_uniques else 'B. Total Events of Scribe Created'
    label = 'Unique First Scribes Created' if is_uniques else 'Total Scribe Events'

    data['hover'] = (
        data['county_name'] + ', ' + data['Region']
        + f'<br>{label}: ' + data[col].apply(lambda x: f'{x:,}')
        + '<br>Cities: ' + data['num_cities'].astype(str)
    )

    z_vals = np.log1p(data[col]) if use_log else data[col]

    colorscale = (
        [[0, '#0d1b2a'], [0.15, '#0e3b5e'], [0.35, '#146b8e'],
         [0.55, '#1a9ec2'], [0.75, '#38bdf8'], [1, '#bae6fd']]
        if is_uniques else
        [[0, '#0d0a1a'], [0.15, '#261454'], [0.35, '#4a2592'],
         [0.55, '#7044d4'], [0.75, '#a78bfa'], [1, '#ddd6fe']]
    )

    # Colorbar ticks
    cb = dict(title=dict(text=label, font=dict(size=13)), len=0.65, thickness=16, tickfont=dict(size=11))
    if use_log:
        max_val = data[col].max()
        ticks = [v for v in [0, 1, 5, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000] if v <= max_val * 1.2]
        cb['tickvals'] = [np.log1p(v) for v in ticks]
        cb['ticktext'] = [f'{v:,}' if v < 1000 else f'{v // 1000}k' for v in ticks]

    fig = go.Figure(go.Choropleth(
        geojson=filtered_geojson,
        locations=data['fips'],
        z=z_vals,
        text=data['hover'],
        hoverinfo='text',
        colorscale=colorscale,
        colorbar=cb,
        marker_line=dict(width=0.3, color='#1e2a3a'),
        hoverlabel=dict(bgcolor='#121825', bordercolor='#1e2a3a',
                        font=dict(size=12, color='#e2e8f0')),
    ))

    geo_opts = dict(
        scope='usa', bgcolor='rgba(0,0,0,0)', lakecolor='#0a0e17',
        landcolor='#0f1520', showlakes=True, showland=True, subunitcolor='#1e2a3a',
    )
    if state_filter and abbr in STATE_CENTERS:
        geo_opts.update(fitbounds='locations', visible=False)
    else:
        geo_opts['projection_type'] = 'albers usa'

    scale_label = "Log Scale" if use_log else "Linear Scale"
    fig.update_layout(
        title=dict(
            text=f'{label}{title_suffix}<br>'
                 f'<span style="font-size:13px;color:#8492a6">'
                 f'Feb 14 2025 → Feb 9 2026 · {len(data)} counties · {scale_label}</span>',
            font=dict(size=20, color='#e2e8f0'),
            x=0.5, xanchor='center',
        ),
        geo=geo_opts,
        paper_bgcolor='#0a0e17',
        plot_bgcolor='#0a0e17',
        font=dict(color='#e2e8f0'),
        margin=dict(t=90, b=20, l=20, r=20),
        height=600,
        width=900,
    )
    return fig


# ---------------------------------------------------------------------------
# STEP 6: Interactive HTML with state dropdown
# ---------------------------------------------------------------------------
def build_interactive_html(county_df, geojson):
    """
    Build a fully self-contained interactive HTML with a state dropdown filter,
    metric toggle, and scale toggle. Great for sharing as a deliverable.
    """
    data = county_df.copy()
    data['hover'] = (
        data['county_name'] + ', ' + data['Region']
        + '<br>Uniques: ' + data['A. Uniques of First Scribe Created'].astype(str)
        + '<br>Total Events: ' + data['B. Total Events of Scribe Created'].apply(lambda x: f'{x:,}')
        + '<br>Cities: ' + data['num_cities'].astype(str)
    )

    # Prepare data as JSON
    records = []
    for _, r in data.iterrows():
        records.append({
            'f': r['fips'],
            'c': r['county_name'],
            's': r['Region'],
            'a': r['state_abbr'],
            'u': int(r['A. Uniques of First Scribe Created']),
            'e': int(r['B. Total Events of Scribe Created']),
            'n': int(r['num_cities']),
            'h': r['hover'],
        })

    data_json = json.dumps(records)
    states_list = json.dumps(sorted(data['Region'].unique().tolist()))

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PLG Scribe Engagement - County Choropleth</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{
            --bg: #0a0e17; --surface: #121825; --border: #1e2a3a;
            --text: #e2e8f0; --dim: #8492a6;
            --blue: #38bdf8; --purple: #a78bfa; --green: #34d399;
        }}
        body {{ font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }}

        .header {{
            padding: 28px 40px 12px;
            border-bottom: 1px solid var(--border);
            background: linear-gradient(180deg, rgba(56,189,248,0.04) 0%, transparent 100%);
        }}
        .header h1 {{
            font-size: 26px; font-weight: 700; letter-spacing: -0.5px;
            background: linear-gradient(135deg, var(--blue), var(--purple));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .header .sub {{
            font-size: 13px; color: var(--dim); margin-top: 4px;
            font-family: 'JetBrains Mono', monospace;
        }}

        .toolbar {{
            display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
            padding: 14px 40px; background: var(--surface); border-bottom: 1px solid var(--border);
        }}
        .toolbar label {{ font-size: 12px; color: var(--dim); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}

        select {{
            background: var(--bg); color: var(--text); border: 1px solid var(--border);
            border-radius: 6px; padding: 7px 12px; font-size: 13px;
            font-family: 'DM Sans', sans-serif; cursor: pointer; outline: none;
        }}
        select:focus {{ border-color: var(--blue); }}

        .btn-group {{
            display: flex; border-radius: 6px; overflow: hidden; border: 1px solid var(--border);
        }}
        .btn {{
            padding: 7px 16px; font-size: 12px; font-family: 'DM Sans', sans-serif;
            font-weight: 600; border: none; background: var(--bg); color: var(--dim);
            cursor: pointer; transition: all 0.15s;
        }}
        .btn:hover:not(.on) {{ color: var(--text); background: rgba(255,255,255,0.04); }}
        .btn.on {{ background: linear-gradient(135deg, var(--blue), var(--purple)); color: #0a0e17; }}

        .sep {{ width: 1px; height: 28px; background: var(--border); margin: 0 4px; }}

        .export-btn {{
            margin-left: auto; padding: 7px 18px; font-size: 12px;
            font-family: 'DM Sans', sans-serif; font-weight: 600;
            border: 1px solid var(--border); border-radius: 6px;
            background: var(--bg); color: var(--green); cursor: pointer; transition: all 0.15s;
        }}
        .export-btn:hover {{ border-color: var(--green); background: rgba(52,211,153,0.08); }}

        .kpis {{
            display: flex; gap: 36px; padding: 14px 40px;
            border-bottom: 1px solid var(--border);
        }}
        .kpi-val {{ font-size: 20px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }}
        .kpi-val.b {{ color: var(--blue); }}
        .kpi-val.p {{ color: var(--purple); }}
        .kpi-lbl {{ font-size: 11px; color: var(--dim); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 1px; }}

        #map {{ width: 100%; height: calc(100vh - 210px); min-height: 500px; }}

        #loader {{
            position: fixed; inset: 0; background: var(--bg);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            z-index: 999; transition: opacity 0.4s;
        }}
        #loader.gone {{ opacity: 0; pointer-events: none; }}
        .spin {{
            width: 36px; height: 36px; border: 3px solid var(--border);
            border-top-color: var(--blue); border-radius: 50%;
            animation: spin 0.7s linear infinite;
        }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        .spin-txt {{ margin-top: 14px; font-size: 13px; color: var(--dim); font-family: 'JetBrains Mono', monospace; }}
    </style>
</head>
<body>

<div id="loader"><div class="spin"></div><div class="spin-txt">Loading county boundaries…</div></div>

<div class="header">
    <h1>PLG Scribe Engagement by County</h1>
    <div class="sub">Feb 14, 2025 → Feb 9, 2026</div>
</div>

<div class="toolbar">
    <label>State</label>
    <select id="stateSelect"><option value="all">All States</option></select>

    <div class="sep"></div>
    <label>Metric</label>
    <div class="btn-group" id="metricBtns">
        <button class="btn on" data-v="both">Both</button>
        <button class="btn" data-v="uniques">Uniques</button>
        <button class="btn" data-v="events">Events</button>
    </div>

    <div class="sep"></div>
    <label>Scale</label>
    <div class="btn-group" id="scaleBtns">
        <button class="btn on" data-v="log">Log</button>
        <button class="btn" data-v="linear">Linear</button>
    </div>

    <button class="export-btn" onclick="exportPNG()">⬇ Export PNG</button>
</div>

<div class="kpis" id="kpis"></div>
<div id="map"></div>

<script>
const ALL_DATA = {data_json};
const STATES = {states_list};

const STATE_CENTERS = {json.dumps(STATE_CENTERS)};
const STATE_ABBREVS = {json.dumps(STATE_ABBREVS)};

let geojson = null;
let metric = 'both';
let scale = 'log';
let stateFilter = 'all';

// Populate state dropdown
const sel = document.getElementById('stateSelect');
STATES.forEach(s => {{ const o = document.createElement('option'); o.value = s; o.textContent = s; sel.appendChild(o); }});
sel.addEventListener('change', () => {{ stateFilter = sel.value; render(); }});

// Button groups
document.querySelectorAll('#metricBtns .btn').forEach(b => {{
    b.addEventListener('click', () => {{
        document.querySelectorAll('#metricBtns .btn').forEach(x => x.classList.remove('on'));
        b.classList.add('on'); metric = b.dataset.v; render();
    }});
}});
document.querySelectorAll('#scaleBtns .btn').forEach(b => {{
    b.addEventListener('click', () => {{
        document.querySelectorAll('#scaleBtns .btn').forEach(x => x.classList.remove('on'));
        b.classList.add('on'); scale = b.dataset.v; render();
    }});
}});

// Load geojson
fetch('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json')
    .then(r => r.json())
    .then(gj => {{ geojson = gj; document.getElementById('loader').classList.add('gone'); render(); }})
    .catch(e => {{ document.querySelector('.spin-txt').textContent = 'Error: ' + e.message; }});

function filteredData() {{
    if (stateFilter === 'all') return ALL_DATA;
    return ALL_DATA.filter(d => d.s === stateFilter);
}}

function filteredGeojson(data) {{
    if (stateFilter === 'all') return geojson;
    const prefixes = new Set(data.map(d => d.f.slice(0, 2)));
    return {{ ...geojson, features: geojson.features.filter(f => prefixes.has(String(f.id).padStart(5,'0').slice(0,2))) }};
}}

function updateKPIs(data) {{
    const tu = data.reduce((s,d) => s+d.u, 0);
    const te = data.reduce((s,d) => s+d.e, 0);
    const topU = data.reduce((b,d) => d.u > b.u ? d : b, data[0] || {{c:'—',u:0}});
    const topE = data.reduce((b,d) => d.e > b.e ? d : b, data[0] || {{c:'—',e:0}});
    document.getElementById('kpis').innerHTML = `
        <div><div class="kpi-val b">${{tu.toLocaleString()}}</div><div class="kpi-lbl">⟶ Sum of All Uniques</div></div>
        <div><div class="kpi-val p">${{te.toLocaleString()}}</div><div class="kpi-lbl">⟶ Sum of All Events</div></div>
        <div><div class="kpi-val" style="color:var(--dim);font-size:16px">${{data.length}}</div><div class="kpi-lbl">Counties · ${{data.reduce((s,d)=>s+d.n,0).toLocaleString()}} cities</div></div>
        <div><div class="kpi-val b" style="font-size:16px">${{topU.c}}</div><div class="kpi-lbl">#1 County · ${{topU.u.toLocaleString()}} uniques</div></div>
        <div><div class="kpi-val p" style="font-size:16px">${{topE.c}}</div><div class="kpi-lbl">#1 County · ${{topE.e.toLocaleString()}} events</div></div>
    `;
}}

const BLUE = [[0,'#0d1b2a'],[0.15,'#0e3b5e'],[0.35,'#146b8e'],[0.55,'#1a9ec2'],[0.75,'#38bdf8'],[1,'#bae6fd']];
const PURPLE = [[0,'#0d0a1a'],[0.15,'#261454'],[0.35,'#4a2592'],[0.55,'#7044d4'],[0.75,'#a78bfa'],[1,'#ddd6fe']];

function colorbar(isU, x) {{
    const data_ = filteredData();
    const vals = data_.map(d => isU ? d.u : d.e);
    const mx = Math.max(...vals, 1);
    const cb = {{ title: {{ text: isU ? 'Uniques' : 'Events', font: {{ size: 12 }} }}, len: 0.55, thickness: 14, x: x, tickfont: {{ size: 10 }} }};
    if (scale === 'log') {{
        const ts = [0,1,5,10,50,100,500,1000,5000,10000,50000,100000].filter(v => v <= mx * 1.2);
        cb.tickvals = ts.map(v => Math.log1p(v));
        cb.ticktext = ts.map(v => v >= 1000 ? (v/1000)+'k' : v.toLocaleString());
    }}
    return cb;
}}

function render() {{
    if (!geojson) return;
    const data = filteredData();
    if (data.length === 0) {{
        Plotly.purge('map');
        document.getElementById('kpis').innerHTML = '<div><div class="kpi-val" style="color:var(--dim)">No data for selected state</div></div>';
        return;
    }}
    updateKPIs(data);
    const gj = filteredGeojson(data);
    const zU = data.map(d => scale === 'log' ? Math.log1p(d.u) : d.u);
    const zE = data.map(d => scale === 'log' ? Math.log1p(d.e) : d.e);
    const fips = data.map(d => d.f);
    const hover = data.map(d => d.h);
    const hl = {{ bgcolor: '#121825', bordercolor: '#1e2a3a', font: {{ size: 12, color: '#e2e8f0' }} }};
    const ml = {{ width: 0.3, color: '#1e2a3a' }};

    const geoBase = {{
        bgcolor: 'rgba(0,0,0,0)', lakecolor: '#0a0e17', landcolor: '#0f1520',
        showlakes: true, showland: true, subunitcolor: '#1e2a3a',
    }};

    let traces, layout;

    if (metric === 'both') {{
        traces = [
            {{ type:'choropleth', geojson:gj, locations:fips, z:zU, text:hover, hoverinfo:'text',
              colorscale:BLUE, colorbar:colorbar(true, 0.44), marker:{{line:ml}}, hoverlabel:hl, geo:'geo' }},
            {{ type:'choropleth', geojson:gj, locations:fips, z:zE, text:hover, hoverinfo:'text',
              colorscale:PURPLE, colorbar:colorbar(false, 1.01), marker:{{line:ml}}, hoverlabel:hl, geo:'geo2' }}
        ];
        const geo = {{ ...geoBase, scope:'usa', domain:{{x:[0, 0.48], y:[0,1]}} }};
        const geo2 = {{ ...geoBase, scope:'usa', domain:{{x:[0.52, 1], y:[0,1]}} }};
        if (stateFilter !== 'all') {{
            geo.fitbounds = 'locations'; geo.visible = false;
            geo2.fitbounds = 'locations'; geo2.visible = false;
        }} else {{
            geo.projection = {{type:'albers usa'}};
            geo2.projection = {{type:'albers usa'}};
        }}
        layout = {{ geo, geo2 }};
    }} else {{
        const isU = metric === 'uniques';
        traces = [
            {{ type:'choropleth', geojson:gj, locations:fips, z:isU?zU:zE, text:hover, hoverinfo:'text',
              colorscale:isU?BLUE:PURPLE, colorbar:colorbar(isU, 1.01), marker:{{line:ml}}, hoverlabel:hl }}
        ];
        const geo = {{ ...geoBase, scope:'usa' }};
        if (stateFilter !== 'all') {{ geo.fitbounds = 'locations'; geo.visible = false; }}
        else {{ geo.projection = {{type:'albers usa'}}; }}
        layout = {{ geo }};
    }}

    layout = {{
        ...layout,
        paper_bgcolor: '#0a0e17', plot_bgcolor: '#0a0e17',
        font: {{ color: '#e2e8f0', family: 'DM Sans' }},
        margin: {{ t: 10, b: 10, l: 10, r: 10 }},
        height: document.getElementById('map').offsetHeight,
    }};

    Plotly.react('map', traces, layout, {{ responsive: true, displayModeBar: false }});
}}

function exportPNG() {{
    Plotly.downloadImage('map', {{
        format: 'png', width: 1600, height: 800, scale: 2,
        filename: 'plg_choropleth_' + stateFilter + '_' + metric
    }});
}}

window.addEventListener('resize', () => Plotly.Plots.resize('map'));
</script>
</body>
</html>'''
    return html


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='PLG County Choropleth Generator')
    parser.add_argument('--csv', default=CSV_PATH, help='Path to CSV file')
    parser.add_argument('--state', default=None, help='Filter to a single state (e.g. "Texas" or "TX")')
    parser.add_argument('--export', default=None, choices=['png', 'pdf', 'html', 'all'],
                        help='Export format (default: open interactive HTML)')
    parser.add_argument('--linear', action='store_true', help='Use linear scale instead of log')
    parser.add_argument('--output-dir', default=OUTPUT_DIR, help='Output directory')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    use_log = not args.linear

    # Process data: use geocoded path if CSV has State FIPS + County FIPS
    if is_geocoded_csv(args.csv):
        county_df = load_and_aggregate_geocoded(args.csv)
    else:
        df = load_data(args.csv)
        df = map_cities_to_counties(df)
        county_df = aggregate_by_county(df)
    geojson = load_geojson()

    state_label = args.state.replace(' ', '_') if args.state else 'all_states'
    scale_label = 'log' if use_log else 'linear'

    if args.export in ('png', 'pdf', 'all') and geojson is None:
        print("\n  ⚠ Static image export requires the GeoJSON file locally.")
        print(f"    Download it first:  curl -o geojson-counties-fips.json {GEOJSON_URL}")
        print("    Then re-run the script. Falling back to HTML export...\n")

    # Always generate interactive HTML (it loads GeoJSON client-side)
    if args.export in (None, 'html', 'all') or geojson is None:
        html = build_interactive_html(county_df, geojson)
        fname = f"{args.output_dir}/plg_choropleth_interactive.html"
        with open(fname, 'w') as f:
            f.write(html)
        print(f"  Exported: {fname}")

    # Static exports (only if GeoJSON is available)
    if geojson and args.export == 'all':
        for m in ['uniques', 'events']:
            fig = build_single_figure(county_df, geojson, metric=m,
                                      state_filter=args.state, use_log=use_log)
            if fig:
                fname = f"{args.output_dir}/plg_{m}_{state_label}_{scale_label}.png"
                fig.write_image(fname, width=1200, height=700, scale=2)
                print(f"  Exported: {fname}")

        fig = build_figure(county_df, geojson, state_filter=args.state, use_log=use_log)
        if fig:
            fname = f"{args.output_dir}/plg_combined_{state_label}_{scale_label}.png"
            fig.write_image(fname, width=1600, height=700, scale=2)
            print(f"  Exported: {fname}")

    elif geojson and args.export in ('png', 'pdf'):
        fig = build_figure(county_df, geojson, state_filter=args.state, use_log=use_log)
        if fig:
            fname = f"{args.output_dir}/plg_choropleth_{state_label}_{scale_label}.{args.export}"
            fig.write_image(fname, width=1600, height=700, scale=2)
            print(f"  Exported: {fname}")

    if args.export is None:
        fname = f"{args.output_dir}/plg_choropleth_interactive.html"
        print(f"\n  Interactive HTML saved to: {fname}")
        print("  Opening in browser...")
        import webbrowser
        webbrowser.open(f'file://{os.path.abspath(fname)}')


if __name__ == '__main__':
    main()
