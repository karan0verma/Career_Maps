import requests
import urllib3
urllib3.disable_warnings()

def test_ntpc():
    urls = [
        "https://careers.ntpc.co.in/",
        "https://ntpc.co.in/careers",
        "https://careers.ntpc.co.in/current_openings.php"
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for url in urls:
        try:
            res = requests.get(url, headers=headers, verify=False, timeout=5)
            print(f"{url} -> Status: {res.status_code}")
            if res.status_code == 200:
                print(res.text[:500])
        except Exception as e:
            print(f"{url} -> Error: {e}")

if __name__ == "__main__":
    test_ntpc()
