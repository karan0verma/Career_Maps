import json
import glob

directory = r"C:\Users\Ahana Singh\.gemini\antigravity\brain\b2157c5e-32e9-4e58-993a-3a6a43a0d53a"
files = glob.glob(f"{directory}\\*_jobs.json")

total = 0
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        count = len(data)
        total += count
        filename = file.split('\\')[-1].replace('_jobs.json', '').upper()
        print(f"{filename}: {count} jobs")

print(f"TOTAL: {total} jobs")
