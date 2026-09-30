import sys
import os
import json
import subprocess
import time

targets = [
    {"domain": "wipro.com", "career_url": "https://careers.wipro.com/careers-home/"},
    {"domain": "hcltech.com", "career_url": "https://www.hcltech.com/careers"},
    {"domain": "paytm.com", "career_url": "https://jobs.lever.co/paytm"},
    {"domain": "barco.com", "career_url": "https://jobs.barco.com/"},
    {"domain": "tcs.com", "career_url": "https://www.tcs.com/careers"},
    {"domain": "globallogic.com", "career_url": "https://www.globallogic.com/careers/"},
    {"domain": "careers.google.com", "career_url": "https://careers.google.com/jobs/results/"},
    {"domain": "usajobs.gov", "career_url": "https://www.usajobs.gov/Search/Results"},
    {"domain": "techcrunch.com", "career_url": "https://techcrunch.com/"}
]

print("--- Real World Verification Phase D ---")

for t in targets:
    domain = t["domain"]
    url = t["career_url"]
    print(f"\nEvaluating: {domain} ({url})")
    
    code = f"""
import json
import logging
logging.basicConfig(level=logging.ERROR)
from src.discovery.models import Target
from src.discovery.detection import StrategySelector
from src.discovery.dispatcher import CrawlerDispatcher
from src.discovery.io import OutputWriter
import dataclasses

class InMemoryWriter(OutputWriter):
    def __init__(self):
        self.jobs = []
    def process(self, target: Target) -> Target:
        return target
    def write_jobs(self, target: Target, jobs: list):
        for job in jobs:
            self.jobs.append(dataclasses.asdict(job) if dataclasses.is_dataclass(job) else job.to_dict() if hasattr(job, 'to_dict') else job)

target = Target(company_name="{domain}", domain="{domain}", career_url="{url}")
selector = StrategySelector()
target = selector.process(target)

writer = InMemoryWriter()
dispatcher = CrawlerDispatcher(writer)
target = dispatcher.process(target)

val = target.metadata.get('validation', {{}})
print(json.dumps({{
    "target": target.to_dict(), 
    "raw_count": val.get('raw_count', 0),
    "valid_count": val.get('valid_count', 0),
    "rejected_count": val.get('rejected_count', 0),
    "duplicates_count": val.get('duplicates_count', 0)
}}))
"""

    start_time = time.time()
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, cwd=os.getcwd()
    )
    duration = time.time() - start_time
    
    lines = result.stdout.strip().split('\n')
    json_output = None
    for line in reversed(lines):
        if line.startswith('{'):
            try:
                json_output = json.loads(line)
                break
            except:
                pass
                
    if json_output:
        t = json_output["target"]
        print(f"Strategy: {t.get('extraction_strategy')}")
        print(f"Raw Candidates: {json_output['raw_count']}")
        print(f"Valid Jobs: {json_output['valid_count']}")
        print(f"Rejected: {json_output['rejected_count']}")
        print(f"Duplicates: {json_output['duplicates_count']}")
        print(f"Time: {duration:.2f}s")
    else:
        print("Failed to run or parse output:")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
