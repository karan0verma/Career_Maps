import requests
import re
urls = [
    "https://stripe.com/in/careers",
    "https://openai.com/careers/",
    "https://www.cloudflare.com/careers/",
    "https://www.notion.so/careers",
    "https://gitlab.com/jobs",
    "https://www.shopify.com/careers",
    "https://www.micron.com/about/careers"
]

for url in urls:
    try:
        html = requests.get(url, timeout=10).text
        print(f"\n--- {url} ---")
        # Look for typical ATS patterns in href or src
        matches = set(re.findall(r'https?://[^\s"\'<>]+', html))
        ats_urls = [m for m in matches if any(x in m.lower() for x in ['lever', 'greenhouse', 'ashby', 'workday', 'smartrecruiters', 'eightfold', 'jobvite', 'bamboohr'])]
        print("Found ATS domains:", ats_urls)
    except Exception as e:
        print(f"Error on {url}: {e}")
