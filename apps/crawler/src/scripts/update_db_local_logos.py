import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company

def set_local_logos():
    db = SessionLocal()
    companies = db.query(Company).all()
    print("=" * 80)
    print("SETTING GUARANTEED 100% OFFLINE LOCAL SVG LOGOS IN DATABASE")
    print("=" * 80)

    mapping = {
        'tata consultancy': '/logos/tcs.svg',
        'tcs': '/logos/tcs.svg',
        'amazon': '/logos/amazon.svg',
        'wipro': '/logos/wipro.svg',
        'hcl': '/logos/hcltech.svg',
        'infosys': '/logos/infosys.svg',
        'cognizant': '/logos/cognizant.svg',
        'tech mahindra': '/logos/techmahindra.svg',
        'oracle': '/logos/oracle.svg',
        'microsoft': '/logos/microsoft.svg',
        'coforge': '/logos/coforge.svg',
    }

    for c in companies:
        name_lower = (c.display_name or c.official_name).lower()
        matched = False
        for key, path in mapping.items():
            if key in name_lower:
                c.logo_url = path
                matched = True
                print(f"  • {c.display_name:30} -> {path}")
                break
        if not matched:
            print(f"  • [No match] {c.display_name:30} -> Keep None (Graceful empty)")

    db.commit()
    print("\nDatabase updated successfully with local /logos/*.svg paths!")
    db.close()

if __name__ == "__main__":
    set_local_logos()
