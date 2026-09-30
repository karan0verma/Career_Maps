import json
import os
import logging
from typing import List, Dict, Any, Set
from .models import Target

logger = logging.getLogger(__name__)

class CheckpointManager:
    def __init__(self, filepath: str = "checkpoint.json", save_every: int = 10, targets: List[Target] = None):
        self.filepath = filepath
        self.save_every = save_every
        self.processed_domains: Set[str] = set()
        self.targets: List[Target] = targets or []
        self.targets_processed_since_save = 0
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_domains = set(data.get("processed_domains", []))
                    if "targets" in data:
                        self.targets = [Target.from_dict(t) for t in data["targets"]]
                logger.info(f"Loaded checkpoint with {len(self.processed_domains)} processed domains.")
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load checkpoint: {e}")

    def save(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "processed_domains": list(self.processed_domains),
                    "targets": [t.to_dict() for t in self.targets]
                }, f, indent=2)
            logger.info(f"Saved checkpoint with {len(self.processed_domains)} domains.")
        except IOError as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def is_processed(self, domain: str) -> bool:
        return domain in self.processed_domains

    def mark_processed(self, domain: str):
        self.processed_domains.add(domain)
        self.targets_processed_since_save += 1
        if self.targets_processed_since_save >= self.save_every:
            self.save()
            self.targets_processed_since_save = 0
