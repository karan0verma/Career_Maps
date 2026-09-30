import requests
import urllib3
urllib3.disable_warnings()

def fetch_ssc():
    url = "https://ssc.gov.in/api/general-website/portal/notice-boards"
    params = {
        "page": 1,
        "limit": 10,
        "contentType": "notice-boards",
        "key": "createdAt",
        "order": "DESC",
        "isAttachment": "true",
        "language": "english"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    res = requests.get(url, params=params, headers=headers, verify=False)
    if res.status_code == 203:
        data = res.json()
        items = data.get('attribute', [])
        print("Found items:", len(items))
        if items:
            for item in items[:5]:
                print(item.get('headline'))
                att = item.get('attachment', {})
                if att:
                    print("https://ssc.gov.in/api/attachment/uploads/master/noticeBoard/" + att.get('fileName', ''))

if __name__ == "__main__":
    fetch_ssc()
