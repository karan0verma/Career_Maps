import json
import os
import logging
import time
from typing import Dict, Any
from .models import Target

logger = logging.getLogger(__name__)

class MetricsAggregator:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.start_time = time.time()
        self.metrics: Dict[str, Any] = {
            "total_targets": 0,
            "career_pages_found": 0,
            "ats_detected_count": {},
            "unsupported_ats": 0,
            "crawl_failures": 0,
            "total_jobs_found": 0,
            "execution_time_seconds": 0
        }

    def add_target(self, target: Target):
        self.metrics["total_targets"] += 1
        
        if target.career_url:
            self.metrics["career_pages_found"] += 1
            
        if target.ats_type:
            ats = target.ats_type
            self.metrics["ats_detected_count"][ats] = self.metrics["ats_detected_count"].get(ats, 0) + 1
        elif target.status == "UNSUPPORTED_ATS":
            self.metrics["unsupported_ats"] += 1
            
        if target.status == "CRAWL_FAILED":
            self.metrics["crawl_failures"] += 1
            
        self.metrics["total_jobs_found"] += target.jobs_discovered

    def finish(self):
        self.metrics["execution_time_seconds"] = round(time.time() - self.start_time, 2)
        
        report_path = os.path.join(self.output_dir, "metrics_report.json")
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2)
            logger.info(f"Metrics report saved to {report_path}")
        except Exception as e:
            logger.error(f"Failed to save metrics report: {e}")
            
        # Also print summary
        logger.info("\n--- Execution Summary ---")
        for k, v in self.metrics.items():
            logger.info(f"{k}: {v}")
