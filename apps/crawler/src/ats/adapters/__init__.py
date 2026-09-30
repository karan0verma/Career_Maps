# Import all adapters here to register them with the AtsRegistry upon initialization

from .workday.crawler import WorkdayCrawler
from .phenom.crawler import PhenomCrawler
from .successfactors_rmk.crawler import SuccessFactorsRmkCrawler
from .greenhouse.crawler import GreenhouseCrawler
from .lever.crawler import LeverCrawler
from .ashby.crawler import AshbyCrawler
from .smartrecruiters.crawler import SmartRecruitersCrawler
from .workable.crawler import WorkableCrawler
from .jobvite.crawler import JobviteCrawler
from .bamboohr.crawler import BambooHRCrawler
from .eightfold.crawler import EightfoldCrawler
from .zohorecruit.crawler import ZohoRecruitCrawler
from .taleo.crawler import TaleoCrawler
from .icims.crawler import ICIMSCrawler

__all__ = [
    'WorkdayCrawler',
    'PhenomCrawler',
    'SuccessFactorsRmkCrawler',
    'GreenhouseCrawler',
    'LeverCrawler',
    'AshbyCrawler',
    'SmartRecruitersCrawler',
    'WorkableCrawler',
    'JobviteCrawler',
    'BambooHRCrawler',
    'EightfoldCrawler',
    'ZohoRecruitCrawler',
    'TaleoCrawler',
    'ICIMSCrawler'
]
