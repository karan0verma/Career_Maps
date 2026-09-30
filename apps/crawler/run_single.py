import sys
import json
import argparse
import os

from src.discovery.career_finder import CareerPageFinder
from src.discovery.detection import StrategySelector
from src.discovery.dispatcher import CrawlerDispatcher
from src.discovery.models import Target
from src.discovery.io import OutputWriter
import dataclasses

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", help="Company domain")
    parser.add_argument("--url", help="Cached career url", default=None)
    parser.add_argument("--strategy", help="Cached extraction strategy", default=None)
    parser.add_argument("--ats", help="Cached ATS type", default=None)
    parser.add_argument('--config', type=str, help='Extraction config JSON string')
    args = parser.parse_args()

    domain = args.domain

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

    target = Target(
        company_name=domain, 
        domain=domain,
        career_url=args.url or "",
        extraction_strategy=args.strategy,
        ats_type=args.ats,
        metadata={"extraction_config": json.loads(args.config)} if args.config else {}
    )
    
    finder = CareerPageFinder()
    selector = StrategySelector()
    writer = InMemoryWriter()
    
    import logging
    
    # Enable debug logs if no URL provided (meaning we are running discovery)
    if not args.url:
        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    # Silence third-party noise if needed
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("WDM").setLevel(logging.ERROR)
    
    if not target.career_url:
        target = finder.process(target)
    
    if not target.extraction_strategy:
        target = selector.process(target)
    
    if target.status != "PENDING":
        print(json.dumps({"target": target.to_dict(), "jobs": []}))
        return

    dispatcher = CrawlerDispatcher(writer)
    
    target = dispatcher.process(target)
    writer.process(target)
    
    result = {
        "target": target.to_dict(),
        "jobs": writer.jobs
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
