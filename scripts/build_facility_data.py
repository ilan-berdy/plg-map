#!/usr/bin/env python3
"""
Build FACILITY_BY_STATE from large_facilities and small_facilities CSVs.
Outputs JavaScript for embedding in index.html.

Usage:
  python scripts/build_facility_data.py \\
    --large "/path/plg_data - large_facilities.csv" \\
    --small "/path/plg_data - small_facilities.csv"
  Then paste the printed object into index.html as FACILITY_BY_STATE.
"""

import csv
import json
import argparse
import os

STATE_ABBREV_TO_FULL = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii',
    'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine',
    'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
    'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska',
    'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
    'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island',
    'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas',
    'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
    'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
}


def load_large_facilities(path):
    """Return dict: state_name -> list of health system names (with facilities in that state)."""
    by_state = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if len(rows) < 4:
        return by_state
    # Row 2 (index 1): "State Name", "", "", then org names
    org_names = []
    for i, cell in enumerate(rows[1]):
        if i >= 3 and cell and cell != 'State Name':
            org_names.append(cell.strip())
    # Rows 4+: state name col 0, counts col 3+
    for row in rows[3:]:
        if len(row) < 4:
            continue
        state_name = row[0].strip()
        if not state_name or state_name == 'total':
            continue
        large = []
        for i in range(3, min(len(row), 3 + len(org_names))):
            try:
                count = int(row[i].strip() or 0)
            except ValueError:
                count = 0
            if count > 0 and (i - 3) < len(org_names):
                large.append(org_names[i - 3])
        by_state[state_name] = {'large': large, 'small': []}
    return by_state


def load_small_facilities(path, by_state):
    """Add small facility names per state. Modifies by_state in place."""
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get('Name') or '').strip()
            abbr = (row.get('State') or '').strip().upper()
            if not name or not abbr or abbr not in STATE_ABBREV_TO_FULL:
                continue
            state_name = STATE_ABBREV_TO_FULL[abbr]
            if state_name not in by_state:
                by_state[state_name] = {'large': [], 'small': []}
            if name and name not in by_state[state_name]['small']:
                by_state[state_name]['small'].append(name)
    return by_state


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--large', required=True, help='Path to large_facilities.csv')
    ap.add_argument('--small', required=True, help='Path to small_facilities.csv')
    ap.add_argument('--max-small', type=int, default=6, help='Max small facility names per state')
    args = ap.parse_args()
    by_state = load_large_facilities(args.large)
    load_small_facilities(args.small, by_state)
    for state in by_state:
        by_state[state]['small'] = by_state[state]['small'][: args.max_small]
    print('const FACILITY_BY_STATE = ' + json.dumps(by_state, indent=2) + ';')


if __name__ == '__main__':
    main()
