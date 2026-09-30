import os
import sys
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company

logos_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\frontend\public\logos"
os.makedirs(logos_dir, exist_ok=True)

# Authentic official corporate logos
authentic_sources = {
    "microsoft": ("microsoft.svg", "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg"),
    "amazon": ("amazon.svg", "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"),
    "oracle": ("oracle.svg", "https://upload.wikimedia.org/wikipedia/commons/5/50/Oracle_logo.svg"),
    "infosys": ("infosys.svg", "https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg"),
    "wipro": ("wipro.svg", "https://upload.wikimedia.org/wikipedia/commons/a/a0/Wipro_Primary_Logo_Color_RGB.svg"),
    "cognizant": ("cognizant.svg", "https://upload.wikimedia.org/wikipedia/commons/4/43/Cognizant_logo_2022.svg"),
    "tcs": ("tcs.svg", "https://upload.wikimedia.org/wikipedia/commons/b/b1/Tata_Consultancy_Services_Logo.svg"),
    "hcl": ("hcltech.svg", "https://upload.wikimedia.org/wikipedia/commons/9/95/HCL_Technologies_logo.svg"),
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

downloaded_logos = {}

for key, (fname, url) in authentic_sources.items():
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200 and ('<svg' in res.text or '<?xml' in res.text):
            fpath = os.path.join(logos_dir, fname)
            with open(fpath, "wb") as f:
                f.write(res.content)
            downloaded_logos[key] = f"/logos/{fname}"
            print(f"  [OK] Downloaded authentic {key.upper()} logo -> /logos/{fname}")
        else:
            print(f"  [FAIL] {key} HTTP {res.status_code}")
    except Exception as e:
        print(f"  [ERR] {key}: {e}")

# Now update Database: set exact path for verified authentic logos, and None for others (khali)
db = SessionLocal()
companies = db.query(Company).all()

print("\nUpdating Database with authentic logos / empty if none:")
for c in companies:
    name_lower = (c.display_name or c.official_name).lower()
    matched = False
    for key, path in downloaded_logos.items():
        if key in name_lower:
            c.logo_url = path
            matched = True
            print(f"  • {c.display_name:30} -> {path}")
            break
    if not matched:
        c.logo_url = None
        print(f"  • {c.display_name:30} -> None (Empty/Khali)")

db.commit()
db.close()
print("\nDone!")
