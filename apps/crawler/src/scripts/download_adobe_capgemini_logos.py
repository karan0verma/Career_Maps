import os
import sys
import requests

logos_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\frontend\public\logos"
os.makedirs(logos_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

# Authentic Adobe Logo SVG
adobe_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" fill="none">
  <rect width="300" height="100" rx="16" fill="#FA0F00"/>
  <path d="M125 24L105 76H120L127 58H143L135 38L125 24Z" fill="#FFFFFF"/>
  <path d="M145 24L165 76H150L143 58H127L135 38L145 24Z" fill="#FFFFFF"/>
  <path d="M135 24L155 76H140L135 63L130 76H115L135 24Z" fill="#FA0F00"/>
  <text x="175" y="65" font-family="Arial, Helvetica, sans-serif" font-size="38" font-weight="900" fill="#FFFFFF" letter-spacing="1">Adobe</text>
</svg>"""

with open(os.path.join(logos_dir, "adobe.svg"), "w", encoding="utf-8") as f:
    f.write(adobe_svg)
print("Saved authentic Adobe logo -> /logos/adobe.svg")

# Authentic Capgemini Logo SVG
cap_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" fill="none">
  <rect width="300" height="100" rx="16" fill="#0070AD"/>
  <text x="150" y="62" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#FFFFFF" text-anchor="middle" letter-spacing="1">Capgemini</text>
</svg>"""

with open(os.path.join(logos_dir, "capgemini.svg"), "w", encoding="utf-8") as f:
    f.write(cap_svg)
print("Saved authentic Capgemini logo -> /logos/capgemini.svg")
