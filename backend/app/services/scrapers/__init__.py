from app.services.scrapers.base import BaseScraper, ScrapedEvent
from app.services.scrapers.dallasites101 import Dallasites101Scraper
from app.services.scrapers.dallas_observer import DallasObserverScraper
from app.services.scrapers.silo_shows import SiloShowsScraper
from app.services.scrapers.visit_dallas import VisitDallasScraper
from app.services.scrapers.x_social import XSocialScraper
from app.services.scrapers.sports_schedules import SportsSchedulesScraper

SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    "dallasites101": Dallasites101Scraper,
    "dallas_observer": DallasObserverScraper,
    "silo_shows": SiloShowsScraper,
    "visit_dallas": VisitDallasScraper,
    "x_social": XSocialScraper,
    "sports_schedules": SportsSchedulesScraper,
}

__all__ = ["BaseScraper", "ScrapedEvent", "SCRAPER_REGISTRY"]
