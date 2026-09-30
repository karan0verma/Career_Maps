import json
import os
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)

class TokenCache(ABC):
    """Abstract base class for ATS board token caching."""
    
    @abstractmethod
    def get(self, ats_type: str, company_url: str) -> Optional[str]:
        pass
        
    @abstractmethod
    def set(self, ats_type: str, company_url: str, token: str) -> None:
        pass


class JsonTokenCache(TokenCache):
    """Temporary JSON-based cache backend for the hardening phase. Can be swapped for Redis later."""
    
    def __init__(self, file_path: str = "logs/token_cache.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
    def _load(self) -> dict:
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load token cache from {self.file_path}: {e}")
            return {}
            
    def _save(self, data: dict) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.warning(f"Failed to save token cache to {self.file_path}: {e}")

    def _make_key(self, ats_type: str, company_url: str) -> str:
        # We strip trailing slashes to normalize slightly
        return f"{ats_type.upper()}:{company_url.rstrip('/')}"

    def get(self, ats_type: str, company_url: str) -> Optional[str]:
        data = self._load()
        key = self._make_key(ats_type, company_url)
        token = data.get(key)
        if token:
            logger.info(f"CACHE HIT: Found {ats_type} token in cache for {company_url}")
        else:
            logger.info(f"CACHE MISS: No {ats_type} token found in cache for {company_url}")
        return token

    def set(self, ats_type: str, company_url: str, token: str) -> None:
        data = self._load()
        key = self._make_key(ats_type, company_url)
        data[key] = token
        self._save(data)
        logger.info(f"CACHE SET: Saved {ats_type} token to cache for {company_url}")
