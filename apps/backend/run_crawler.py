import sys
import json
import argparse
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../crawler')))

from src.discovery.career_finder import CareerPageFinder
from src.discovery.detection import ATSDetectionEngine
from src.discovery.dispatcher import CrawlerDispatcher
from src.discovery.models import Target
from src.discovery.io import OutputWriter
import dataclasses

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", help="Company domain")
    args = parser.parse_args()

    domain = args.domain

    # Create dummy output writer that just collects jobs in memory
    class InMemoryWriter(OutputWriter):
        def __init__(self):
            self.jobs = []
            
        def process(self, target: Target) -> Target:
            if target.status == "PENDING":
                target.status = "SUCCESS" if target.jobs_discovered > 0 else "COMPLETED_EMPTY"
            return target
            
        def write_jobs(self, target: Target, jobs: list):
            for job in jobs:
                jdict = None
                if isinstance(job, dict):
                    jdict = job
                elif dataclasses.is_dataclass(job):
                    jdict = dataclasses.asdict(job)
                elif hasattr(job, 'to_dict'):
                    jdict = job.to_dict()
                    
                if jdict is not None:
                    jdict['company_name'] = target.company_name
                    jdict['domain'] = target.domain
                    self.jobs.append(jdict)

    target = Target(company_name=domain, domain=domain)
    
    finder = CareerPageFinder()
    detector = ATSDetectionEngine()
    writer = InMemoryWriter()
    
    target = finder.process(target)
    target = detector.process(target)
    
    if target.status != "PENDING":
        print(json.dumps({"target": target.to_dict(), "jobs": []}))
        return

    dispatcher = CrawlerDispatcher(writer)
    # the dispatcher will call writer.write_jobs
    
    # We patch the submission so it doesn't do legacy submission
    # By intercepting before submit
    target = dispatcher.process(target)
    writer.process(target)
    
    result = {
        "target": target.to_dict(),
        "jobs": writer.jobs
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
