import sys
import os
import json
import subprocess
import time

targets = [
    {"domain": "usajobs.gov", "career_url": "https://www.usajobs.gov/Search/Results"},
    {"domain": "careers.google.com", "career_url": "https://careers.google.com/jobs/results/"}
]

print("--- Real World Verification Phase C ---")

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

print(json.dumps({{"target": target.to_dict(), "jobs_found": len(writer.jobs), "jobs": writer.jobs[:2]}}))
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
        print(f"Jobs Found: {json_output['jobs_found']}")
        if json_output["jobs"]:
            print(f"Sample Job: {json_output['jobs'][0].get('title')} ({json_output['jobs'][0].get('applyUrl')})")
        print(f"Status: {t.get('status')}")
        print(f"Errors: {t.get('errors')}")
        print(f"Time: {duration:.2f}s")
    else:
        print("Failed to run or parse output:")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
