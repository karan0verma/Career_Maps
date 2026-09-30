import unittest
from unittest.mock import patch, MagicMock
from src.discovery.models import Target
from src.discovery.career_finder import CareerPageFinder
from src.discovery.detection import ATSDetectionEngine
from src.discovery.io import InputReader, OutputWriter

class TestDiscoveryCLI(unittest.TestCase):
    def test_target_model(self):
        t = Target(company_name="Test", domain="test.com")
        self.assertEqual(t.status, "PENDING")
        self.assertEqual(t.jobs_discovered, 0)
        
    @patch('requests.Session.head')
    def test_career_finder_common_paths(self, mock_head):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.url = "https://test.com/careers"
        mock_head.return_value = mock_response
        
        finder = CareerPageFinder()
        t = Target(company_name="Test", domain="test.com")
        t = finder.process(t)
        
        self.assertEqual(t.career_url, "https://test.com/careers")
        
    def test_ats_detection_engine(self):
        detector = ATSDetectionEngine()
        
        t = Target(company_name="Lever", domain="lever.co", career_url="https://jobs.lever.co/lever")
        t = detector.process(t)
        self.assertEqual(t.ats_type, "LEVER")
        
        t2 = Target(company_name="Greenhouse", domain="greenhouse.io", career_url="https://boards.greenhouse.io/test")
        t2 = detector.process(t2)
        self.assertEqual(t2.ats_type, "GREENHOUSE")

if __name__ == '__main__':
    unittest.main()
