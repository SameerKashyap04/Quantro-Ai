import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ScreenerScraper:
    """
    Scrapes fundamental analysis data from Screener.in and Trendlyne.
    Note: These sites may have bot protections. We use basic User-Agent spoofing.
    """
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

    @classmethod
    def fetch_screener_in_fundamentals(cls, symbol: str) -> Dict[str, Any]:
        """
        Attempts to scrape fundamental ratios from Screener.in
        e.g. https://www.screener.in/company/RELIANCE/consolidated/
        """
        url = f"https://www.screener.in/company/{symbol.upper()}/consolidated/"
        try:
            res = requests.get(url, headers=cls.HEADERS, timeout=10)
            if res.status_code != 200:
                logger.warning(f"Screener.in returned {res.status_code} for {symbol}. Possibly blocked by Cloudflare.")
                # Fallback to non-consolidated
                url = f"https://www.screener.in/company/{symbol.upper()}/"
                res = requests.get(url, headers=cls.HEADERS, timeout=10)
                if res.status_code != 200:
                    return {}
            
            soup = BeautifulSoup(res.text, "html.parser")
            company_ratios = {}
            
            # Find the top ratios section
            ratios_ul = soup.find("ul", id="top-ratios")
            if ratios_ul:
                for li in ratios_ul.find_all("li"):
                    name_span = li.find("span", class_="name")
                    value_span = li.find("span", class_="number")
                    if name_span and value_span:
                        name = name_span.text.strip()
                        val_str = value_span.text.strip().replace(",", "")
                        try:
                            val = float(val_str)
                            company_ratios[name] = val
                        except ValueError:
                            company_ratios[name] = val_str
                            
            return company_ratios
        except Exception as e:
            logger.error(f"Error scraping Screener.in for {symbol}: {e}")
            return {}

    @classmethod
    def fetch_trendlyne_metrics(cls, symbol: str) -> Dict[str, Any]:
        """
        Attempts to fetch Trendlyne momentum and DVM scores.
        Note: Trendlyne uses heavy dynamic rendering. This is a best-effort HTML parse.
        """
        # We would typically need a full headless browser (Playwright) for Trendlyne
        # due to their heavy React/Next.js hydration, but we can attempt a basic scrape.
        url = f"https://trendlyne.com/stock/{symbol.upper()}/"
        try:
            res = requests.get(url, headers=cls.HEADERS, timeout=10)
            if res.status_code != 200:
                return {}
            
            # This is a placeholder for trendlyne data. In reality, their DOM is obfuscated.
            # We would parse the DVM scores if they were in the raw HTML.
            return {"trendlyne_status": "Scraped (Basic)"}
            
        except Exception as e:
            logger.error(f"Error scraping Trendlyne for {symbol}: {e}")
            return {}
