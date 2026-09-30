import unittest
from unittest.mock import MagicMock, patch
import requests

from src.services.submission_service import VirtualList, SubmissionService
from src.base_crawler import BaseCrawler
from src.dto.crawler_context import CrawlerContext
from src.http_crawler import HttpCrawler

class TestHardening(unittest.TestCase):
    
    def test_virtual_list(self):
        """Test the O(1) memory list replacement."""
        vlist = VirtualList(50000)
        self.assertEqual(len(vlist), 50000)
        self.assertIsNone(vlist[0])
        self.assertIsNone(vlist[49999])
        
        with self.assertRaises(IndexError):
            _ = vlist[50000]
            
        count = 0
        for item in VirtualList(10):
            self.assertIsNone(item)
            count += 1
        self.assertEqual(count, 10)

    def test_submission_service(self):
        """Ensure the service returns VirtualList objects."""
        svc = SubmissionService({"opportunities": []})
        result = svc.process_and_submit([])
        
        self.assertIsInstance(result["newOpportunities"], VirtualList)
        self.assertEqual(len(result["newOpportunities"]), 0)

    class MockCrawler(BaseCrawler):
        def __init__(self, data):
            super().__init__(data)
            self.crawl_calls = 0

        def login(self, context):
            pass

        def crawl(self, context):
            self.crawl_calls += 1
            # Simulate a transient 500 error
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            raise requests.exceptions.HTTPError(response=mock_resp)
            
        def parse(self, data):
            return []
            
        def normalize(self, data):
            return []

    @patch('src.base_crawler.BaseCrawler.random_delay')
    def test_transient_retry_logic(self, mock_delay):
        crawler = self.MockCrawler({"companyName": "Test", "id": "test"})
        crawler.max_retries = 2
        
        with self.assertRaises(requests.exceptions.HTTPError):
            crawler._execute_lifecycle(CrawlerContext())
            
        # 1 initial try + 2 retries = 3 total calls
        self.assertEqual(crawler.crawl_calls, 3)

    class MockCrawlerFatal(BaseCrawler):
        def __init__(self, data):
            super().__init__(data)
            self.crawl_calls = 0

        def login(self, context):
            pass

        def crawl(self, context):
            self.crawl_calls += 1
            # Simulate a fatal 404 error
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            raise requests.exceptions.HTTPError(response=mock_resp)
            
        def parse(self, data):
            return []
            
        def normalize(self, data):
            return []

    @patch('src.base_crawler.BaseCrawler.random_delay')
    def test_fatal_no_retry_logic(self, mock_delay):
        crawler = self.MockCrawlerFatal({"companyName": "Test", "id": "test"})
        crawler.max_retries = 2
        
        with self.assertRaises(requests.exceptions.HTTPError):
            crawler._execute_lifecycle(CrawlerContext())
            
        # 1 initial try, NO retries because 404 is not transient
        self.assertEqual(crawler.crawl_calls, 1)


if __name__ == '__main__':
    unittest.main()
