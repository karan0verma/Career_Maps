import logging
from typing import Dict, Any
from .models import Target
from .pipeline import PipelineStage
from src.ats.registry import AtsRegistry
from .io import OutputWriter

# Import adapters so they register themselves
from src.ats.adapters import *

logger = logging.getLogger(__name__)

class CrawlerDispatcher(PipelineStage):
    def __init__(self, output_writer: OutputWriter):
        self.output_writer = output_writer

    def process(self, target: Target) -> Target:
        if target.status != "PENDING" and target.status != "DRY_RUN_COMPLETED":
            return target
            
        if not target.extraction_strategy:
            logger.info(f"[{target.domain}] Skipping crawler dispatch: No extraction strategy selected.")
            return target
            
        if target.extraction_strategy == "KNOWN_ATS":
            if not target.ats_type:
                logger.warning(f"[{target.domain}] Strategy is KNOWN_ATS but ats_type is missing.")
                target.status = "UNSUPPORTED_ATS"
                return target
                
            CrawlerClass = AtsRegistry.get(target.ats_type)
            if not CrawlerClass:
                logger.warning(f"[{target.domain}] ATS '{target.ats_type}' is registered but has no adapter class in AtsRegistry.")
                target.status = "UNSUPPORTED_ATS"
                return target
        elif target.extraction_strategy == "STRUCTURED_JSON_LD":
            from src.extractors.structured_data_extractor import StructuredDataExtractor
            CrawlerClass = StructuredDataExtractor
        elif target.extraction_strategy == "GENERIC_API":
            from src.extractors.api_extractor import APIExtractor
            CrawlerClass = APIExtractor
        elif target.extraction_strategy == "GENERIC_DOM":
            from src.extractors.generic_dom_extractor import GenericDOMExtractor
            CrawlerClass = GenericDOMExtractor
        else:
            logger.info(f"[{target.domain}] Strategy '{target.extraction_strategy}' is unknown. Skipping extraction.")
            target.status = "FAILED"
            return target
            
        logger.info(f"[{target.domain}] Dispatching {CrawlerClass.__name__} for {target.career_url}")
        
        # Build the configuration dict expected by HttpCrawler/PlaywrightCrawler
        config = {
            "companyName": target.company_name,
            "id": target.domain.replace(".", "_"),
            "officialCareerPage": target.career_url,
            "atsType": target.ats_type,
            "metadata": target.metadata
        }
        logger.info(f"[{target.domain}] Crawler config metadata: {config['metadata']}")
        
        crawler = CrawlerClass(config)
        
        try:
            jobs = crawler.execute()
            
            # Validation Phase (Phase D)
            from src.validators.job_validator import JobValidator
            validator = JobValidator()
            valid_jobs, rejected_jobs, duplicates_count = validator.process(target, jobs)
            
            target.jobs_discovered = len(valid_jobs)
            target.metadata['validation'] = {
                'raw_count': len(jobs),
                'valid_count': len(valid_jobs),
                'rejected_count': len(rejected_jobs),
                'duplicates_count': duplicates_count
            }
            
            if rejected_jobs:
                logger.info(f"[{target.domain}] Rejected {len(rejected_jobs)} jobs. Top rejection: {rejected_jobs[0]}")
            
            if target.jobs_discovered > 0:
                self.output_writer.write_jobs(target, valid_jobs)
                
                # Now pass to submission service to simulate O(1) memory backend flush
                crawler.submit(valid_jobs)
                
                target.status = "SUCCESS"
            else:
                target.status = "COMPLETED_EMPTY"
                
            logger.info(f"[{target.domain}] Crawl successful. Found {target.jobs_discovered} valid jobs.")
            
        except Exception as e:
            logger.error(f"[{target.domain}] Crawl failed: {e}")
            target.status = "CRAWL_FAILED"
            target.errors.append(str(e))
            
        return target
