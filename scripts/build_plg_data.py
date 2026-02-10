#!/usr/bin/env python3
"""
Build data/plg_data.js from a geocoded PLG CSV that includes EHR (e.g. "c. EHR").
Use this CSV as the source of truth; index.html loads plg_data.js for ALL_DATA and SUMMARIES.

Usage:
    python scripts/build_plg_data.py [path/to/raw_data.csv]
    Default CSV path: ../data/PLG_User_Count_Insights.csv (or same CSV with EHR + State/County FIPS)

Output: data/plg_data.js (ALL_DATA, SUMMARIES with optional EHR and top EHRs per state).
"""

import json
import os
import sys
from collections import Counter

import pandas as pd

# Reuse state mapping
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
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
}


def normalize_ehr(s):
    if pd.isna(s) or s is None:
        return None
    t = str(s).strip()
    if not t or t.lower() in ('nan', 'undefined', 'none'):
        return None
    return t


def load_and_build(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df = df[~df['Region'].isin(['undefined', 'Region'])].copy()
    df['state_abbr'] = df['Region'].map(STATE_ABBREVS)
    df = df.dropna(subset=['state_abbr'])

    # FIPS
    df['State FIPS'] = pd.to_numeric(df['State FIPS'], errors='coerce')
    df['County FIPS'] = pd.to_numeric(df['County FIPS'], errors='coerce')
    df = df.dropna(subset=['State FIPS', 'County FIPS'])
    state_str = df['State FIPS'].astype(int).astype(str).str.zfill(2)
    county_str = df['County FIPS'].astype(int).astype(str).str[-3:].str.zfill(3)
    df['fips'] = state_str + county_str

    df['uniques'] = pd.to_numeric(df['A. Uniques of First Scribe Created'], errors='coerce').fillna(0).astype(int)
    df['events'] = pd.to_numeric(df['B. Total Events of Scribe Created'], errors='coerce').fillna(0).astype(int)

    # EHR column: accept "c. EHR" or any column containing "EHR"
    ehr_col = None
    for c in df.columns:
        if 'ehr' in c.lower():
            ehr_col = c
            break
    if ehr_col:
        df['ehr_raw'] = df[ehr_col].apply(normalize_ehr)
    else:
        df['ehr_raw'] = None

    county_name_col = 'Geocodio County' if 'Geocodio County' in df.columns else None
    df['county_name'] = df[county_name_col].fillna('').astype(str) if county_name_col else ''

    # County-level aggregation: sum uniques/events, count cities, collect EHR (top by events)
    def top_ehrs(grp, top_n=5):
        if grp['ehr_raw'].isna().all() or grp['ehr_raw'].eq('').all():
            return []
        by_ehr = grp.groupby(grp['ehr_raw'].fillna('')).agg(events=('events', 'sum')).sort_values('events', ascending=False)
        return by_ehr.index[by_ehr.index != ''].tolist()[:top_n]

    county_agg = df.groupby(['fips', 'county_name', 'Region', 'state_abbr']).agg(
        uniques=('uniques', 'sum'),
        events=('events', 'sum'),
        num_cities=('City', 'count'),
    ).reset_index()
    county_agg['fips'] = county_agg['fips'].astype(str).str.zfill(5)
    county_agg['county_name'] = county_agg.apply(
        lambda r: r['county_name'] if r['county_name'] else f"County {r['fips'][2:]}",
        axis=1,
    )

    # Per-county top EHRs (from raw rows)
    ehr_by_county = df.groupby('fips', group_keys=False).apply(lambda g: top_ehrs(g, top_n=5))
    ehr_dict = ehr_by_county.to_dict()
    county_agg['ehr_list'] = county_agg['fips'].map(lambda f: ehr_dict.get(f, []))

    # ALL_DATA records
    records = []
    for _, r in county_agg.iterrows():
        ehr_str = ', '.join(r['ehr_list']) if r['ehr_list'] else ''
        hover = (
            f"{r['county_name']}, {r['Region']}<br>Clinicians: {r['uniques']}<br>"
            f"Patient Visits: {r['events']:,}<br>Cities: {r['num_cities']}"
        )
        if ehr_str:
            hover += f"<br>EHR: {ehr_str}"
        rec = {
            'f': r['fips'],
            'c': r['county_name'],
            's': r['Region'],
            'a': r['state_abbr'],
            'u': int(r['uniques']),
            'e': int(r['events']),
            'n': int(r['num_cities']),
            'h': hover,
        }
        if ehr_str:
            rec['ehr'] = ehr_str
        records.append(rec)

    # SUMMARIES: state-level from city-level (use raw df for cities)
    city_agg = (
        df.groupby(['Region', 'City'])
        .agg(
            clinicians=('uniques', 'sum'),
            visits=('events', 'sum'),
        )
        .reset_index()
    )
    summaries = {}
    for state in city_agg['Region'].unique():
        st = city_agg[city_agg['Region'] == state]
        clinicians = int(st['clinicians'].sum())
        visits = int(st['visits'].sum())
        total_cities = len(st)
        active_cities = int((st['clinicians'] > 0).sum())
        top_cities = (
            st.nlargest(5, 'clinicians')[['City', 'clinicians', 'visits']]
            .rename(columns={'City': 'city', 'clinicians': 'clinicians', 'visits': 'visits'})
            .to_dict('records')
        )
        for row in top_cities:
            row['visits'] = int(row['visits'])
            row['clinicians'] = int(row['clinicians'])

        state_df = df[df['Region'] == state]
        top_ehrs_state = []
        if 'ehr_raw' in state_df.columns and state_df['ehr_raw'].notna().any():
            by_ehr = (
                state_df.groupby(state_df['ehr_raw'].fillna(''))
                .agg(events=('events', 'sum'))
                .sort_values('events', ascending=False)
            )
            top_ehrs_state = [x for x in by_ehr.index if x and str(x).strip()][:5]

        summaries[state] = {
            'clinicians': clinicians,
            'visits': visits,
            'totalCities': total_cities,
            'activeCities': active_cities,
            'topCities': top_cities,
        }
        if top_ehrs_state:
            summaries[state]['topEhrs'] = top_ehrs_state

    return records, summaries


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    default_csv = os.path.join(repo_root, 'data', 'PLG_User_Count_Insights.csv')
    csv_path = sys.argv[1] if len(sys.argv) > 1 else default_csv
    if not os.path.isfile(csv_path):
        print(f"Error: CSV not found: {csv_path}")
        sys.exit(1)

    out_path = os.path.join(repo_root, 'data', 'plg_data.js')
    records, summaries = load_and_build(csv_path)
    print(f"Built {len(records)} counties, {len(summaries)} states from {csv_path}")

    states_list = sorted(summaries.keys())
    js_content = (
        "// Generated by scripts/build_plg_data.py — do not edit by hand.\n"
        "window.ALL_DATA = " + json.dumps(records) + ";\n"
        "window.STATES = " + json.dumps(states_list) + ";\n"
        "window.SUMMARIES = " + json.dumps(summaries) + ";\n"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        f.write(js_content)
    print(f"Wrote {out_path}")


if __name__ == '__main__':
    main()
