from playwright.sync_api import sync_playwright
import json

def test_pages():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("--- Eightfold AI ---")
        try:
            # intercept network to see JSON payloads
            def handle_response(response):
                if "api/apply/v2/jobs" in response.url:
                    print(f"Eightfold API Status: {response.status}")
                    try:
                        print("Eightfold API Keys:", response.json().keys())
                        if 'positions' in response.json() and len(response.json()['positions']) > 0:
                            pos = response.json()['positions'][0]
                            print("Eightfold first position:", {k: type(v).__name__ for k, v in pos.items()})
                    except Exception as e:
                        pass
                
                if "Job_Openings" in response.url or "recruit" in response.url:
                    if response.request.resource_type in ["xhr", "fetch"]:
                        print(f"Zoho API Status ({response.url}): {response.status}")
                        try:
                            data = response.json()
                            print("Zoho API JSON keys:", data.keys() if isinstance(data, dict) else type(data))
                            if isinstance(data, dict) and 'data' in data:
                                if len(data['data']) > 0:
                                    print("Zoho first job keys:", data['data'][0].keys())
                        except Exception as e:
                            pass

            page.on("response", handle_response)
            
            page.goto("https://micron.eightfold.ai/careers", wait_until="networkidle", timeout=20000)
            page.wait_for_timeout(2000)
            
            print("\n--- Zoho Recruit ---")
            page.goto("https://zohocorp.zohorecruit.com/jobs/Careers", wait_until="networkidle", timeout=20000)
            page.wait_for_timeout(2000)
            
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

test_pages()
