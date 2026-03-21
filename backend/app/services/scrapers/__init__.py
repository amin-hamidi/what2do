from app.services.scrapers.base import BaseScraper, ScrapedEvent
from app.services.scrapers.dallasites101 import Dallasites101Scraper

SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    "dallasites101": Dallasites101Scraper,
}

__all__ = ["BaseScraper", "ScrapedEvent", "SCRAPER_REGISTRY"]
