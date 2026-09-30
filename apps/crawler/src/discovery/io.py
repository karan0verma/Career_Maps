import csv
import json
import os
from typing import Iterator
from .models import Target
from .pipeline import PipelineStage

class InputReader:
    @staticmethod
    def read_csv(filepath: str) -> Iterator[Target]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Input file not found: {filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                domain = row.get("domain", "").strip()
                company_name = row.get("company_name", domain).strip()
                career_url = row.get("career_url", "").strip() or None
                if domain:
                    yield Target(company_name=company_name, domain=domain, career_url=career_url)

    @staticmethod
    def read_txt(filepath: str) -> Iterator[Target]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Input file not found: {filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                domain = line.strip()
                if domain:
                    yield Target(company_name=domain, domain=domain)


class OutputWriter(PipelineStage):
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.jobs_file = os.path.join(self.output_dir, "jobs.jsonl")
        
    def process(self, target: Target) -> Target:
        # We don't write to jobs.jsonl here; that's handled by CrawlerDispatcher passing jobs to OutputWriter explicitly if needed
        # Or we can write the execution report row here.
        # But per requirements, jobs are serialized during crawl.
        # This stage ensures the Target status is finalized for the report.
        if target.status == "PENDING":
            target.status = "SUCCESS" if target.jobs_discovered > 0 else "COMPLETED_EMPTY"
            
        # Write execution log
        log_file = os.path.join(self.output_dir, "execution_report.jsonl")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(target.to_dict()) + "\n")
            
        return target
        
    def write_jobs(self, target: Target, jobs: list):
        import dataclasses
        with open(self.jobs_file, 'a', encoding='utf-8') as f:
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
                    f.write(json.dumps(jdict) + "\n")
