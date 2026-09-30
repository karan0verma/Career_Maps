import requests

def test_api():
    url = "https://careers.cognizant.com/widgets"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers)
        print("Widgets status:", res.status_code)
    except:
        pass
        
    url2 = "https://careers.cognizant.com/api/jobs"
    try:
        res2 = requests.get(url2, headers=headers)
        print("API jobs status:", res2.status_code)
    except:
        pass

if __name__ == "__main__":
    test_api()
