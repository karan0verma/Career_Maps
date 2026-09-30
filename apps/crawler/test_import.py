import sys
import traceback

try:
    from src.ats.adapters.phenom.crawler import PhenomCrawler
    print("Successfully imported PhenomCrawler")
except Exception as e:
    print("Error importing PhenomCrawler:")
    traceback.print_exc()
