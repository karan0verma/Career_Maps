import os
import sys

logos_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\frontend\public\logos"
os.makedirs(logos_dir, exist_ok=True)

# Clean, professional vector SVGs for each tech giant

svg_logos = {
    "tcs.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" fill="none">
  <rect width="300" height="100" rx="16" fill="#003366"/>
  <text x="150" y="62" font-family="Arial, Helvetica, sans-serif" font-size="44" font-weight="900" fill="#FFFFFF" text-anchor="middle" letter-spacing="4">TCS</text>
  <text x="150" y="82" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#00C4CC" text-anchor="middle" letter-spacing="2">TATA CONSULTANCY SERVICES</text>
</svg>""",

    "amazon.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" fill="none">
  <rect width="300" height="100" rx="16" fill="#131921"/>
  <text x="150" y="55" font-family="Arial, Helvetica, sans-serif" font-size="38" font-weight="bold" fill="#FFFFFF" text-anchor="middle">amazon</text>
  <path d="M 90 68 Q 150 90 210 68" stroke="#FF9900" stroke-width="6" stroke-linecap="round" fill="none"/>
  <polygon points="208,63 218,68 212,77" fill="#FF9900"/>
</svg>""",

    "microsoft.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" fill="none">
  <rect width="300" height="100" rx="16" fill="#FFFFFF" stroke="#E5E7EB" stroke-width="2"/>
  <g transform="translate(35, 26)">
    <rect x="0" y="0" width="22" height="22" fill="#F25022"/>
    <rect x="26" y="0" width="22" height="22" fill="#7FBA00"/>
    <rect x="0" y="26" width="22" height="22" fill="#00A4EF"/>
    <rect x="26" y="26" width="22" height="22" fill="#FFB900"/>
  </g>
  <text x="98" y="60" font-family="Segoe UI, Arial, sans-serif" font-size="32" font-weight="600" fill="#737373">Microsoft</text>
</svg>""",

    "oracle.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" fill="none">
  <rect width="300" height="100" rx="16" fill="#C74634"/>
  <text x="150" y="64" font-family="Arial, Helvetica, sans-serif" font-size="44" font-weight="900" fill="#FFFFFF" text-anchor="middle" letter-spacing="6">ORACLE</text>
</svg>""",

    "infosys.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" fill="none">
  <rect width="300" height="100" rx="16" fill="#007CC3"/>
  <text x="150" y="62" font-family="Arial, Helvetica, sans-serif" font-size="40" font-weight="bold" fill="#FFFFFF" text-anchor="middle" letter-spacing="1">Infosys</text>
  <text x="150" y="80" font-family="Arial, sans-serif" font-size="9" font-weight="bold" fill="#FFFFFF" text-anchor="middle" letter-spacing="3">NAVIGATE YOUR NEXT</text>
</svg>""",

    "wipro.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" fill="none">
  <rect width="300" height="100" rx="16" fill="#FFFFFF" stroke="#E5E7EB" stroke-width="2"/>
  <g transform="translate(35, 25)">
    <circle cx="25" cy="25" r="16" fill="#4B0082" opacity="0.8"/>
    <circle cx="35" cy="18" r="12" fill="#E6007E" opacity="0.8"/>
    <circle cx="38" cy="32" r="10" fill="#009F4D" opacity="0.8"/>
    <circle cx="20" cy="35" r="8" fill="#F39200" opacity="0.8"/>
  </g>
  <text x="95" y="60" font-family="Arial, Helvetica, sans-serif" font-size="36" font-weight="bold" fill="#2E1A47">wipro</text>
</svg>""",

    "hcltech.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" fill="none">
  <rect width="300" height="100" rx="16" fill="#0D2C54"/>
  <text x="150" y="63" font-family="Arial, Helvetica, sans-serif" font-size="38" font-weight="900" fill="#FFFFFF" text-anchor="middle" letter-spacing="2">HCL<tspan fill="#3B82F6">Tech</tspan></text>
  <text x="150" y="82" font-family="Arial, sans-serif" font-size="9" font-weight="bold" fill="#60A5FA" text-anchor="middle" letter-spacing="2">SUPERCHARGING PROGRESS</text>
</svg>""",

    "cognizant.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" fill="none">
  <rect width="300" height="100" rx="16" fill="#0033A0"/>
  <text x="150" y="63" font-family="Arial, Helvetica, sans-serif" font-size="36" font-weight="bold" fill="#FFFFFF" text-anchor="middle" letter-spacing="1">Cognizant</text>
</svg>""",

    "techmahindra.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" fill="none">
  <rect width="300" height="100" rx="16" fill="#FFFFFF" stroke="#E5E7EB" stroke-width="2"/>
  <g transform="translate(25, 25)">
    <rect x="0" y="5" width="40" height="40" rx="8" fill="#D32F2F"/>
    <text x="20" y="33" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#FFFFFF" text-anchor="middle">M</text>
  </g>
  <text x="80" y="48" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#D32F2F">Tech</text>
  <text x="80" y="68" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#333333">Mahindra</text>
</svg>""",

    "coforge.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" fill="none">
  <rect width="300" height="100" rx="16" fill="#FFFFFF" stroke="#E5E7EB" stroke-width="2"/>
  <text x="150" y="63" font-family="Arial, Helvetica, sans-serif" font-size="38" font-weight="bold" fill="#E65100" text-anchor="middle" letter-spacing="2">Coforge</text>
</svg>"""
}

for fname, content in svg_logos.items():
    fpath = os.path.join(logos_dir, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created local SVG logo: {fpath}")

print("\nAll 10 local SVG logos created successfully!")
