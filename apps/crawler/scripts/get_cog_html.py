import requests

def get_cog_html():
    res = requests.get("https://careers.cognizant.com/global-en/jobs/")
    print(res.text[:1000])
    
    # search for pcsDomain or similar API endpoint
    import re
    matches = re.findall(r'https?://[a-zA-Z0-9.-]+\.cognizant\.com[a-zA-Z0-9./-]*', res.text)
    print("Found domains/endpoints:", list(set(matches)))

if __name__ == "__main__":
    get_cog_html()
