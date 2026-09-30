from typing import Optional, List
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from urllib.parse import urlparse, urljoin
import logging
from .models import Target
from .pipeline import PipelineStage

logger = logging.getLogger(__name__)

class DiscoveryStrategy(ABC):
    """Abstract strategy for finding a career page."""
    
    def __init__(self, session: requests.Session):
        self.session = session

    @abstractmethod
    def execute(self, domain: str) -> Optional[str]:
        """Returns the career URL if found, else None."""
        pass

class CommonPathsStrategy(DiscoveryStrategy):
    def execute(self, domain: str) -> Optional[str]:
        paths = ["/careers", "/jobs", "/about/careers"]
        for path in paths:
            url = f"https://{domain}{path}"
            try:
                resp = self.session.get(url, timeout=5, allow_redirects=True)
                if resp.status_code == 200:
                    return resp.url
            except requests.RequestException:
                continue
        return None

class SubdomainStrategy(DiscoveryStrategy):
    def execute(self, domain: str) -> Optional[str]:
        subdomains = ["careers", "jobs"]
        for sub in subdomains:
            url = f"https://{sub}.{domain}/"
            try:
                resp = self.session.get(url, timeout=5, allow_redirects=True)
                if resp.status_code == 200:
                    return resp.url
            except requests.RequestException:
                continue
        return None

class HomepageLinksStrategy(DiscoveryStrategy):
    def execute(self, domain: str) -> Optional[str]:
        url = f"https://{domain}/"
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code != 200:
                return None
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                text = a.get_text().strip().lower()
                href = a.get('href', '')
                if text in ["careers", "jobs", "join us"]:
                    if href.startswith('http'):
                        return href
                    else:
                        return urljoin(resp.url, href)
        except requests.RequestException:
            return None
            
        return None

class GoogleSearchStrategy(DiscoveryStrategy):
    def execute(self, domain: str) -> Optional[str]:
        # Quick google search fallback
        company_name = domain.split('.')[0]
        url = f"https://www.google.com/search?q={company_name}+careers"
        try:
            resp = self.session.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'url?q=' in href and 'google' not in href:
                    clean_url = href.split('url?q=')[1].split('&')[0]
                    if domain in clean_url or 'careers' in clean_url.lower() or 'jobs' in clean_url.lower():
                        return clean_url
        except requests.RequestException:
            pass
        return None

class DirectCareerDomainStrategy(DiscoveryStrategy):
    def execute(self, domain: str) -> Optional[str]:
        if "jobs" in domain or "career" in domain:
            url = f"https://{domain}/"
            try:
                resp = self.session.get(url, timeout=5, allow_redirects=True)
                if resp.status_code == 200:
                    return resp.url
            except requests.RequestException:
                pass
        return None

class CareerPageFinder(PipelineStage):
    def __init__(self):
        self.session = requests.Session()
        from fake_useragent import UserAgent
        ua = UserAgent()
        self.session.headers.update({
            "User-Agent": ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        })
        self.strategies: List[DiscoveryStrategy] = [
            DirectCareerDomainStrategy(self.session),
            CommonPathsStrategy(self.session),
            SubdomainStrategy(self.session),
            HomepageLinksStrategy(self.session),
            GoogleSearchStrategy(self.session)
        ]
        
    def process(self, target: Target) -> Target:
        if target.career_url:
            return target # Already resolved
            
        logger.info(f"[{target.domain}] Running CareerPageFinder...")
        
        for strategy in self.strategies:
            logger.debug(f"[{target.domain}] Trying {strategy.__class__.__name__}...")
            url = strategy.execute(target.domain)
            if url:
                logger.info(f"[{target.domain}] Found career page: {url}")
                target.career_url = url
                return target
                
        logger.info(f"[{target.domain}] Career page not found.")
        target.status = "NOT_FOUND"
        target.errors.append("Career page discovery exhausted all strategies.")
        return target
