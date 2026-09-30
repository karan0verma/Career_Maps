import argparse
import sys
import logging
from .io import InputReader, OutputWriter
from .models import Target

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class CLIController:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Discovery CLI")
        subparsers = self.parser.add_subparsers(dest="command")
        
        # scan command
        scan_parser = subparsers.add_parser("scan", help="Scan a list of companies/domains")
        scan_parser.add_argument("input_file", help="Path to input CSV or TXT file")
        scan_parser.add_argument("--dry-run", action="store_true", help="Run without executing crawlers")
        
        # company command
        company_parser = subparsers.add_parser("company", help="Process a single company domain")
        company_parser.add_argument("domain", help="Target domain")
        company_parser.add_argument("--dry-run", action="store_true", help="Run without executing crawler")
        
        # resume command
        resume_parser = subparsers.add_parser("resume", help="Resume from a checkpoint")
        resume_parser.add_argument("checkpoint_file", help="Path to checkpoint.json")
        resume_parser.add_argument("--dry-run", action="store_true", help="Run without executing crawlers")
        
        # validate command
        validate_parser = subparsers.add_parser("validate", help="Validate input file")
        validate_parser.add_argument("input_file", help="Path to input CSV or TXT file")

    def run(self, args_list=None):
        args = self.parser.parse_args(args_list)
        
        if not args.command:
            self.parser.print_help()
            return
            
        logger.info(f"Executing command: {args.command}")
        
        targets = []
        
        if args.command == "scan":
            targets = list(self._load_file(args.input_file))
        elif args.command == "company":
            targets = [Target(company_name=args.domain, domain=args.domain)]
        elif args.command == "validate":
            targets = list(self._load_file(args.input_file))
            logger.info(f"Validated {len(targets)} targets.")
            return
        elif args.command == "resume":
            logger.info(f"Resuming from checkpoint: {args.checkpoint_file}")
            targets = self._load_checkpoint(args.checkpoint_file)
            if not targets:
                logger.info("No uncompleted targets found in checkpoint.")
                return
            
        self._execute_pipeline(targets, getattr(args, 'dry_run', False))

    def _load_checkpoint(self, filepath: str):
        from .checkpoint import CheckpointManager
        manager = CheckpointManager(filepath=filepath)
        return manager.targets

    def _load_file(self, filepath: str):
        if filepath.endswith('.csv'):
            return InputReader.read_csv(filepath)
        else:
            return InputReader.read_txt(filepath)

    def _execute_pipeline(self, targets, dry_run: bool):
        from .career_finder import CareerPageFinder
        from .detection import ATSDetectionEngine
        from .checkpoint import CheckpointManager
        from .metrics import MetricsAggregator
        
        finder = CareerPageFinder()
        detector = ATSDetectionEngine()
        writer = OutputWriter()
        checkpoint = CheckpointManager(targets=targets)
        metrics = MetricsAggregator()
        
        try:
            for t in targets:
                if checkpoint.is_processed(t.domain):
                    logger.info(f"Skipping {t.domain} (already processed)")
                    continue
                    
                logger.info(f"Processing: {t.domain}")
                t = finder.process(t)
                t = detector.process(t)
                
                if dry_run:
                    logger.info(f"[{t.domain}] Dry run: skipping crawler dispatcher.")
                    if t.status == "PENDING":
                        t.status = "DRY_RUN_COMPLETED"
                else:
                    from .dispatcher import CrawlerDispatcher
                    dispatcher = CrawlerDispatcher(writer)
                    t = dispatcher.process(t)
                    
                writer.process(t)
                checkpoint.mark_processed(t.domain)
                metrics.add_target(t)
        except KeyboardInterrupt:
            logger.info("Received interrupt. Saving checkpoint and metrics...")
        finally:
            checkpoint.save()
            metrics.finish()
            
if __name__ == "__main__":
    cli = CLIController()
    cli.run()
