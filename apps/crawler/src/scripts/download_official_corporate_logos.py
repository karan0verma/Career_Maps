import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company

logos_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\frontend\public\logos"
os.makedirs(logos_dir, exist_ok=True)

# Direct verified brand asset endpoints
official_brand_pages = {
    "cognizant": ("cognizant.svg", "https://www.cognizant.com"),
    "wipro": ("wipro.svg", "https://www.wipro.com"),
    "tcs": ("tcs.svg", "https://www.tcs.com"),
    "hcl": ("hcltech.svg", "https://www.hcltech.com"),
    "techmahindra": ("techmahindra.svg", "https://www.techmahindra.com"),
    "coforge": ("coforge.svg", "https://www.coforge.com"),
}

downloaded = {}

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    page = context.new_page()

    for key, (fname, site_url) in official_brand_pages.items():
        try:
            print(f"Fetching official logo from {site_url}...", flush=True)
            page.goto(site_url, wait_until='domcontentloaded', timeout=20000)
            time.sleep(2)

            # Find main logo image / svg
            logo_src = page.evaluate("""() => {
                const logoImg = document.querySelector('header img, a[class*="logo"] img, .navbar-brand img, img[alt*="logo" i], header svg, .logo svg');
                if (logoImg) {
                    if (logoImg.tagName.toLowerCase() === 'svg') {
                        return { type: 'svg', content: logoImg.outerHTML };
                    }
                    return { type: 'img', src: logoImg.src };
                }
                return null;
            }""")

            if logo_src:
                fpath = os.path.join(logos_dir, fname)
                if logo_src.get('type') == 'svg' and logo_src.get('content'):
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(logo_src['content'])
                    downloaded[key] = f"/logos/{fname}"
                    print(f"  [OK] Saved authentic SVG from {key} header!")
                elif logo_src.get('src'):
                    res = page.request.get(logo_src['src'])
                    if res.ok:
                        ext = '.svg' if 'svg' in logo_src['src'] else '.png'
                        actual_fname = fname.replace('.svg', ext)
                        actual_path = os.path.join(logos_dir, actual_fname)
                        with open(actual_path, "wb") as f:
                            f.write(res.body())
                        downloaded[key] = f"/logos/{actual_fname}"
                        print(f"  [OK] Downloaded authentic {actual_fname} from {site_url}!")
            else:
                print(f"  [Notice] No logo found on {site_url}, leaving clean/empty.")

        except Exception as e:
            print(f"  [Error] {key}: {e}")

    browser.close()

# Update DB
db = SessionLocal()
companies = db.query(Company).all()

# Pre-existing authentic ones
downloaded['microsoft'] = '/logos/microsoft.svg'
downloaded['amazon'] = '/logos/amazon.svg'
downloaded['oracle'] = '/logos/oracle.svg'
downloaded['infosys'] = '/logos/infosys.svg'

print("\nUpdating Database with only authentic official logos:")
for c in companies:
    name_lower = (c.display_name or c.official_name).lower()
    matched = False
    for key, path in downloaded.items():
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
print("\nAll database records updated!")
