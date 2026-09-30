import requests

def test_icims():
    print("\n--- iCIMS ---")
    url = "https://careers-icims.icims.com/jobs/search?ss=1"
    try:
        resp = requests.get(url, timeout=5)
        print("Status:", resp.status_code)
        print("Length:", len(resp.text))
        if "schema.org" in resp.text:
            print("Contains schema.org data (SSR)")
    except Exception as e:
        print(e)

def test_eightfold():
    print("\n--- Eightfold AI ---")
    # Eightfold is heavily frontend driven
    url = "https://careers.eightfold.ai/api/apply/v2/jobs"
    try:
        resp = requests.get(url, params={"domain": "eightfold.com"}, timeout=5)
        print("Status:", resp.status_code)
        if resp.status_code == 200:
            print("Keys:", resp.json().keys())
    except Exception as e:
        print(e)

def test_zoho():
    print("\n--- Zoho Recruit ---")
    url = "https://zoho.zohorecruit.com/recruit/v2/public/Job_Openings"
    try:
        resp = requests.get(url, timeout=5)
        print("Status:", resp.status_code)
        if resp.status_code == 200:
            print("Data:", str(resp.json())[:100])
    except Exception as e:
        print(e)

def test_darwinbox():
    print("\n--- Darwinbox ---")
    url = "https://careers.darwinbox.com/jobs"
    try:
        resp = requests.get(url, timeout=5)
        print("Status:", resp.status_code)
        if "csrf" in resp.text.lower():
            print("Uses CSRF token")
    except Exception as e:
        print(e)

test_icims()
test_eightfold()
test_zoho()
test_darwinbox()
