import requests

companies = ["asana", "soundcloud", "canva", "wix", "foursquare", "patreon", "lyft", "grammarly", "databricks", "snowflake", "datarobot", "hashicorp", "okta", "zscaler", "mongodb", "elastic", "datadog", "splunk", "atlassian", "twilio", "zoom", "postman", "figma", "notion", "airtable"]

for c in companies:
    try:
        url = f"https://{c}.bamboohr.com/careers/list"
        resp = requests.get(url, headers={'Accept': 'application/json'}, timeout=5)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if 'result' in data and len(data['result']) > 0:
                    print(f"[{c}] SUCCESS! Found jobs: {len(data['result'])}")
                    print(f"First job keys: {list(data['result'][0].keys())}")
                    print(f"First job: {data['result'][0]}")
                    break
            except:
                pass
    except:
        pass
