from src.registry import CrawlerRegistry
CrawlerRegistry.load_crawlers()
print(CrawlerRegistry._registry)
