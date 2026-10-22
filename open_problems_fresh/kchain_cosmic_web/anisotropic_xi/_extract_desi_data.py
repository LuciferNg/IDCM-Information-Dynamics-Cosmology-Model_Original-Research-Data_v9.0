#!/usr/bin/env python3
"""
Extract DESI DR2 BAO data and correlation function data from the paper text.
"""
import re, json

with open('/home/wsl/IDCM/sync_bump_analysis/desi_dr2_bao.txt', 'r') as f:
    text = f.read()

# ================================================================
# 1. BAO 測量數據
# ================================================================
print("=" * 80)
print("  DESI DR2 BAO 測量數據")
print("=" * 80)

# Search for the main BAO table
# Look for sections with DM/rd, DH/rd
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'DM/rd' in line and ('DH/rd' in line or 'DV/rd' in line):
        print(f"\n  Found table header at line {i}:")
        print(f"  {line[:200]}")
        # Print surrounding lines
        for j in range(max(0, i-2), min(len(lines), i+50)):
            l = lines[j].strip()
            if l and ('DM' in l or 'DH' in l or 'DV' in l or 'zeff' in l.lower() or 'χ²' in l or 'LRG' in l or 'ELG' in l or 'QSO' in l or 'Lyα' in l or 'z=' in l or '±' in l):
                print(f"  {j}: {l[:200]}")

print("\n\n")

# Alternative: look for numeric tables
for i, line in enumerate(lines):
    if 'z_eff' in line.lower() or 'zeff' in line.lower() or 'effective redshift' in line.lower():
        print(f"  Found z_eff mention at line {i}: {line[:200]}")
        for j in range(i, min(len(lines), i+30)):
            l = lines[j].strip()
            if l and len(l) > 10:
                print(f"  {j}: {l[:200]}")

print("\n\n")

# Search for correlation function / multipole / ξ(s) data
for i, line in enumerate(lines):
    if any(kw in line.lower() for kw in ['correlation function', 'multipole', 'ξ(s)', 'xi(s)', 'monopole', 'quadrupole']):
        print(f"  Found at line {i}: {line[:200]}")
        for j in range(i, min(len(lines), i+5)):
            l = lines[j].strip()
            if l:
                print(f"    {j}: {l[:200]}")

print("\n\n")

# Search for data release / data access
for i, line in enumerate(lines):
    if any(kw in line.lower() for kw in ['data release', 'zenodo', 'data access', 'https://', 'github.com/desi']):
        print(f"  Found at line {i}: {line[:200]}")

print("\n\n")

# Look for the actual BAO numbers
# Pattern: z=0.51, DM/rd=12.99±0.19 etc.
for i, line in enumerate(lines):
    if 'DM/rd' in line and '±' in line:
        print(f"  BAO data at line {i}: {line[:200]}")

# Also look for the BAO table in the separate text file
print("\n--- DESI DR2 BAO MAIN ---")
with open('/home/wsl/IDCM/sync_bump_analysis/desi_dr2_bao_main.txt', 'r') as f:
    main_text = f.read()
    
# Find table-like data
main_lines = main_text.split('\n')
for i, line in enumerate(main_lines):
    if any(kw in line.lower() for kw in ['table', 'dm/rd', 'dh/rd', 'dv/rd', 'α', 'alpha', 'zeff', 'z_eff']):
        print(f"  {i}: {line[:200]}")
        for j in range(i+1, min(len(main_lines), i+20)):
            l = main_lines[j].strip()
            if l and not l.startswith('|') and not l.startswith('arXiv'):
                # Check if it looks like data
                if any(c.isdigit() for c in l) and len(l) > 20:
                    print(f"    {j}: {l[:200]}")
                else:
                    break

print("\n\n--- DESI DR2 BAO TABLES ---")
with open('/home/wsl/IDCM/sync_bump_analysis/desi_dr2_bao_tables.txt', 'r') as f:
    tables_text = f.read()

# Find the actual table
table_lines = tables_text.split('\n')
for i, line in enumerate(table_lines):
    if any(kw in line.lower() for kw in ['table 1', 'table 2', 'table 3', 'table 4', 'table 5', 'dm/rd', 'dh/rd']):
        print(f"  {i}: {line[:200]}")
        for j in range(i+1, min(len(table_lines), i+30)):
            l = table_lines[j].strip()
            if l and len(l) > 10:
                # Filter out headers and empty lines
                if not l.startswith('|') and not l.startswith('arXiv') and not l.startswith('DESI'):
                    print(f"    {j}: {l[:200]}")