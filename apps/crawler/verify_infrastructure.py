import logging
from src.http_crawler import HttpCrawler
from src.services.html_parser.service import HtmlParserService
from src.services.xml_parser.service import XmlParserService
from src.services.token_discovery.service import TokenDiscoveryService
from src.dto.crawler_context import CrawlerContext
import requests
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)

class DummyHttpCrawler(HttpCrawler):
    def __init__(self):
        super().__init__({"companyName": "Test", "id": "test", "officialCareerPage": ""})
        
def run_infrastructure_tests():
    crawler = DummyHttpCrawler()
    session = crawler._create_session()
    context = CrawlerContext(session=session)
    
    print("\n--- Testing HtmlParserService & HTML Fetching ---")
    mock_html = '''
    <html>
      <body>
        <script>var config = {"api_key": "12345"};</script>
        <input type="hidden" name="csrf_token" value="abcde">
        <iframe src="https://app.jobvite.com/CompanyJobs/Careers.aspx?c=qyV9VfwP"></iframe>
      </body>
    </html>
    '''
    
    token = HtmlParserService.regex_search(mock_html, r'[\?&]c=([a-zA-Z0-9]+)')
    print(f"Jobvite Token Regex Extraction: {token}")
    
    hidden = HtmlParserService.extract_hidden_inputs(mock_html)
    print(f"Hidden Inputs: {hidden}")
    
    script_json = HtmlParserService.extract_json_from_script(mock_html, r'var config = (\{.*?\});')
    print(f"Script JSON: {script_json}")
    
    print("\n--- Testing XmlParserService & XML Fetching ---")
    mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <result>
        <job id="123">
            <title>Software Engineer</title>
            <location>San Francisco, CA</location>
            <department>Engineering</department>
        </job>
        <job id="456">
            <title>Product Manager</title>
            <location>New York, NY</location>
            <department>Product</department>
        </job>
    </result>
    '''
    
    root = XmlParserService.parse_string(mock_xml)
    print(f"Parsed XML Root Tag: {root.tag if root is not None else 'None'}")
    
    if root is not None:
        jobs = XmlParserService.find_all_elements(root, ".//job")
        print(f"Found {len(jobs)} jobs in XML.")
        if jobs:
            job_dict = XmlParserService.node_to_dict(jobs[0])
            print(f"First Job Dict: {job_dict}")
    
if __name__ == "__main__":
    run_infrastructure_tests()
