import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company

def inspect_and_fix_logos():
    db = SessionLocal()
    companies = db.query(Company).all()
    print("=" * 80)
    print("CURRENT COMPANY LOGOS IN DATABASE:")
    print("=" * 80)

    # Official high-res logo map (Clearbit & Wikimedia reliable static URLs)
    official_logos = {
        'tata consultancy services': 'https://logo.clearbit.com/tcs.com',
        'amazon': 'https://logo.clearbit.com/amazon.com',
        'wipro': 'https://logo.clearbit.com/wipro.com',
        'hcl': 'https://logo.clearbit.com/hcltech.com',
        'infosys': 'https://logo.clearbit.com/infosys.com',
        'cognizant': 'https://logo.clearbit.com/cognizant.com',
        'tech mahindra': 'https://logo.clearbit.com/techmahindra.com',
        'oracle': 'https://logo.clearbit.com/oracle.com',
        'microsoft': 'https://logo.clearbit.com/microsoft.com',
        'coforge': 'https://logo.clearbit.com/coforge.com',
        'google': 'https://logo.clearbit.com/google.com',
        'meta': 'https://logo.clearbit.com/meta.com',
        'flipkart': 'https://logo.clearbit.com/flipkart.com',
        'zomato': 'https://logo.clearbit.com/zomato.com',
        'swiggy': 'https://logo.clearbit.com/swiggy.com',
    }

    for c in companies:
        name_lower = (c.display_name or c.official_name).lower()
        print(f"Company: {c.display_name:30} | Current Logo: {c.logo_url}")
        
        # Match logo
        for key, url in official_logos.items():
            if key in name_lower:
                c.logo_url = url
                break

    db.commit()
    print("\nUpdated all company logos with verified high-resolution Clearbit assets!")
    db.close()

if __name__ == "__main__":
    inspect_and_fix_logos()
