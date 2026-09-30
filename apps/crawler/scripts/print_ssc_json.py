import requests
import urllib3
import json
urllib3.disable_warnings()

def print_ssc_json():
    url = "https://ssc.gov.in/api/general-website/portal/notice-boards"
    params = {
        "page": 1,
        "limit": 10,
        "contentType": "notice-boards",
        "key": "createdAt",
        "order": "DESC",
        "isAttachment": "true",
        "language": "english",
        "attributes": "id,headline,examId,contentType,redirectUrl,startDate,endDate,language,createdAt"
    }
    res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
    print(json.dumps(res.json(), indent=2)[:1000])

if __name__ == "__main__":
    print_ssc_json()
