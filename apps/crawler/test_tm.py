from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://careers.techmahindra.com/CurrentOpportunity.aspx')
    page.wait_for_timeout(5000)
    
    # Try clicking search
    try:
        page.click("input[type='submit'][value='Search']")
        page.wait_for_timeout(5000)
    except:
        print("No search button found.")
        
    links = page.evaluate("Array.from(document.querySelectorAll('a')).map(a => a.href)")
    job_links = [l for l in links if 'JobDetails.aspx' in l]
    print('Job links found:', len(job_links))
    browser.close()
