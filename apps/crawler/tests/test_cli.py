import unittest
import os
import json
from src.discovery.models import Target
from src.discovery.checkpoint import CheckpointManager

class TestDiscoveryCLI(unittest.TestCase):
    
    def test_target_serialization(self):
        t1 = Target(company_name="Test", domain="test.com", ats_type="LEVER", status="COMPLETED")
        t_dict = t1.to_dict()
        self.assertEqual(t_dict["domain"], "test.com")
        self.assertEqual(t_dict["status"], "COMPLETED")
        
        t2 = Target.from_dict(t_dict)
        self.assertEqual(t2.company_name, "Test")
        self.assertEqual(t2.ats_type, "LEVER")
        self.assertEqual(t2.status, "COMPLETED")

    def test_checkpoint_manager_persistence(self):
        filepath = "test_checkpoint.json"
        if os.path.exists(filepath):
            os.remove(filepath)
            
        t1 = Target(company_name="Test", domain="test.com")
        t2 = Target(company_name="OpenAI", domain="openai.com")
        
        cm = CheckpointManager(filepath=filepath, save_every=1, targets=[t1, t2])
        cm.mark_processed("test.com")
        
        # Verify it saved
        self.assertTrue(os.path.exists(filepath))
        
        # Load from new instance
        cm2 = CheckpointManager(filepath=filepath)
        self.assertTrue(cm2.is_processed("test.com"))
        self.assertFalse(cm2.is_processed("openai.com"))
        
        self.assertEqual(len(cm2.targets), 2)
        self.assertEqual(cm2.targets[1].domain, "openai.com")
        
        os.remove(filepath)

if __name__ == '__main__':
    unittest.main()
