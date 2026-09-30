import requests
import re

url = "https://jobs.jobvite.com/fivetran"
html = requests.get(url).text

print("Searching for 'company' in HTML...")
matches = re.findall(r'[\'"]([a-zA-Z0-9]+)[\'"]', html)
# Let's just find the actual string "qyV9VfwP" if it exists, or maybe we don't know the hash for fivetran.
# Let's find any unique looking 8-char hashes.
hashes = set(re.findall(r'[\'"]([a-zA-Z0-9]{8,12})[\'"]', html))
print(f"Hashes: {hashes}")

print("Checking Jobvite specific vars:")
matches3 = re.findall(r'jv[\w_]*\s*[:=]\s*[\'"]?([a-zA-Z0-9]+)[\'"]?', html, re.IGNORECASE)
print(f"jv vars: {matches3}")

print("Checking scripts")
import bs4
soup = bs4.BeautifulSoup(html, "html.parser")
for s in soup.find_all("script"):
    if s.string and "fivetran" in s.string.lower():
        print("Script with fivetran:")
        print(s.string[:200])
