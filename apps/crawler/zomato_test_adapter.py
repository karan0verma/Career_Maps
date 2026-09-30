from src.crawlers.zomato_crawler import ZomatoCrawler

def test_zomato_adapter():
    company_data = {
        "companyName": "Zomato",
        "id": "zomato_123",
        "officialCareerPage": "https://www.zomato.com/careers",
        "opportunities": []
    }
    
    crawler = ZomatoCrawler(company_data)
    # Reducing max_retries for quick testing
    crawler.max_retries = 0 
    
    result = crawler.execute()
    print("Crawl Result:", result)

if __name__ == "__main__":
    test_zomato_adapter()
