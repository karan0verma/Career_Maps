import os
import sys
import json

staging_path = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging\DOUBLE_CHECK_STAGING_REPORT.json"

with open(staging_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 1. Adobe Engineering & Product breakdown
adobe_jobs = data["companies"]["Adobe"]["all_jobs"]
print("=" * 80)
print(f"ADOBE INDIA JOBS ANALYSIS (Total Staged: {len(adobe_jobs)})")
print("=" * 80)

eng_keywords = ['engineer', 'software', 'developer', 'architect', 'qa', 'sdet', 'data', 'ml', 'ai', 'cloud', 'security', 'tech', 'full stack', 'backend', 'frontend']
prod_keywords = ['product manager', 'product management', 'product designer', 'designer', 'ux', 'ui', 'program manager', 'technical program manager', 'solutions', 'strategy']

adobe_engineering = []
adobe_product = []
adobe_others = []

for j in adobe_jobs:
    t = j['title'].lower()
    is_eng = any(k in t for k in eng_keywords)
    is_prod = any(k in t for k in prod_keywords)
    
    if is_eng:
        adobe_engineering.append(j)
    elif is_prod:
        adobe_product.append(j)
    else:
        adobe_others.append(j)

print(f"  • Engineering & Tech Roles: {len(adobe_engineering)}")
print(f"  • Product, Design & Program Management Roles: {len(adobe_product)}")
print(f"  • Total Engineering + Product Roles: {len(adobe_engineering) + len(adobe_product)} (out of {len(adobe_jobs)})")
print(f"  • Other Business / Consulting / Sales Roles: {len(adobe_others)}")

print("\nSample Adobe Engineering Roles:")
for j in adobe_engineering[:5]:
    print(f"    - {j['title']} ({j['location']})")

print("\nSample Adobe Product Roles:")
for j in adobe_product[:5]:
    print(f"    - {j['title']} ({j['location']})")

# 2. Capgemini Bengaluru breakdown
cap_jobs = data["companies"]["Capgemini"]["all_jobs"]
print("\n" + "=" * 80)
print(f"CAPGEMINI INDIA JOBS ANALYSIS (Total Staged: {len(cap_jobs)})")
print("=" * 80)

cap_bengaluru = []
cap_other_cities = {}

for j in cap_jobs:
    loc = j['location'].lower()
    if 'bangalore' in loc or 'bengaluru' in loc:
        cap_bengaluru.append(j)
    else:
        city = j['location'].split(',')[0].strip()
        cap_other_cities[city] = cap_other_cities.get(city, 0) + 1

print(f"  • Bengaluru / Bangalore Roles: {len(cap_bengaluru)} (out of {len(cap_jobs)})")
print(f"  • Other Major Cities Breakdown: {cap_other_cities}")

print("\nSample Capgemini Bengaluru Roles:")
for j in cap_bengaluru[:5]:
    print(f"    - {j['title']} (URL: {j['apply_url']})")
