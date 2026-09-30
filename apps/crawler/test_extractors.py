import json
import logging
from src.extractors.structured_data_extractor import StructuredDataExtractor
from src.extractors.api_extractor import APIExtractor
from src.extractors.generic_dom_extractor import GenericDOMExtractor

def test_structured_data():
    print("Testing StructuredDataExtractor...")
    extractor = StructuredDataExtractor({"companyName": "TestCo", "id": "test_co"})
    
    # 1. Single JobPosting
    html1 = '''<html><body><script type="application/ld+json">
    {
      "@type": "JobPosting",
      "title": "Software Engineer",
      "description": "Develop stuff.",
      "identifier": {"value": "REQ-123"},
      "jobLocation": {"address": {"addressLocality": "San Francisco", "addressRegion": "CA", "addressCountry": "US"}}
    }
    </script></body></html>'''
    
    parsed1 = extractor.parse(html1)
    normalized1 = extractor.normalize(parsed1)
    assert len(normalized1) == 1
    assert normalized1[0].title == "Software Engineer"
    assert normalized1[0].externalJobId == "REQ-123"
    assert "San Francisco" in normalized1[0].location
    print("  [x] Single JobPosting")
    
    # 2. @graph
    html2 = '''<html><body><script type="application/ld+json">
    {
      "@graph": [
          {"@type": "JobPosting", "title": "Data Scientist"},
          {"@type": "Organization", "name": "TestCo"}
      ]
    }
    </script></body></html>'''
    parsed2 = extractor.parse(html2)
    normalized2 = extractor.normalize(parsed2)
    assert len(normalized2) == 1
    assert normalized2[0].title == "Data Scientist"
    print("  [x] @graph JobPosting")
    
def test_api_extractor():
    print("Testing APIExtractor...")
    extractor = APIExtractor({"companyName": "TestCo", "id": "test_co"})
    
    # Simple array
    data1 = [
        {"title": "DevOps", "jobId": "999", "location": "Remote"}
    ]
    extracted1 = extractor._extract_job_list(data1)
    norm1 = extractor.normalize(extracted1)
    assert len(norm1) == 1
    assert norm1[0].title == "DevOps"
    assert norm1[0].externalJobId == "999"
    print("  [x] Simple array")
    
    # Nested array
    data2 = {
        "success": True,
        "results": {
            "jobs": [
                {"role": "Product Manager", "id": "PM1", "city": "NY", "summary": "Manage products"}
            ]
        }
    }
    extracted2 = extractor._extract_job_list(data2)
    norm2 = extractor.normalize(extracted2)
    assert len(norm2) == 1
    assert norm2[0].title == "Product Manager"
    print("  [x] Nested array")
    
    # Unrelated JSON
    data3 = [{"news_title": "Update", "author": "Alice"}]
    extracted3 = extractor._extract_job_list(data3)
    assert len(extracted3) == 0
    print("  [x] Unrelated JSON rejection")

def test_dom_extractor():
    print("Testing GenericDOMExtractor (Parse logic)...")
    extractor = GenericDOMExtractor({"companyName": "TestCo", "id": "test_co"})
    
    data = [
        {"text": "Software Engineer", "href": "https://careers.test/job/1"},
        {"text": "About Us", "href": "https://test/about"},
        {"text": "Find a Job", "href": "https://careers.test/jobs"},
        {"text": "Lead Data Analyst", "href": "https://careers.test/job/2"}
    ]
    parsed = extractor.parse(data)
    norm = extractor.normalize(parsed)
    assert len(norm) == 2
    assert norm[0].title == "Software Engineer"
    assert norm[1].title == "Lead Data Analyst"
    print("  [x] DOM Extractor heuristics")

if __name__ == "__main__":
    test_structured_data()
    test_api_extractor()
    test_dom_extractor()
    print("All unit tests passed!")
