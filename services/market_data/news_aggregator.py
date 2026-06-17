import feedparser
import requests
import logging
from typing import List, Dict
from bs4 import BeautifulSoup
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class NewsAggregator:
    """
    Aggregates financial news from multiple premium sources via RSS.
    """
    RSS_FEEDS = {
        "moneycontrol": "https://www.moneycontrol.com/rss/MCtopnews.xml",
        "moneycontrol_buzzing": "https://www.moneycontrol.com/rss/buzzingstocks.xml",
        "economic_times": "https://economictimes.indiatimes.com/markets/rssfeeds/19770215.cms",
        "mint": "https://www.livemint.com/rss/markets"
    }

    @staticmethod
    def fetch_rss_feed(url: str, publisher: str, symbol: str = None) -> List[Dict]:
        """Fetch and parse an RSS feed, optionally filtering by symbol."""
        try:
            feed = feedparser.parse(url)
            results = []
            for entry in feed.entries:
                title = entry.title
                # Simple keyword filter if a symbol is provided
                if symbol and symbol.lower() not in title.lower() and symbol.lower() not in entry.get('summary', '').lower():
                    continue
                
                # Parse timestamp if available
                pub_time = 0
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_time = int(time.mktime(entry.published_parsed))

                results.append({
                    "title": title,
                    "publisher": publisher,
                    "link": entry.link,
                    "providerPublishTime": pub_time
                })
            return results
        except Exception as e:
            logger.error(f"Failed to fetch RSS feed {url}: {e}")
            return []

    @classmethod
    def fetch_all_news(cls, symbol: str, limit: int = 5) -> List[Dict]:
        """Fetch news from Yahoo Finance + Indian RSS Feeds."""
        all_news = []
        
        # 1. Indian RSS Feeds (filter by symbol keyword)
        # Note: Since RSS feeds only contain current top news, it's possible the symbol won't be mentioned today.
        # So we also pull general market news if no specific symbol is matched, or we rely on yfinance for symbol-specific news.
        mc_news = cls.fetch_rss_feed(cls.RSS_FEEDS["moneycontrol_buzzing"], "Moneycontrol", symbol)
        et_news = cls.fetch_rss_feed(cls.RSS_FEEDS["economic_times"], "Economic Times", symbol)
        mint_news = cls.fetch_rss_feed(cls.RSS_FEEDS["mint"], "Mint", symbol)
        
        all_news.extend(mc_news)
        all_news.extend(et_news)
        all_news.extend(mint_news)

        # 2. Yahoo Finance (global baseline, specifically targeted to the ticker)
        from services.market_data.fetchers import YFinanceFetcher
        # Note: We must avoid circular import if fetchers imports us, so import here inline
        try:
            yf_news = YFinanceFetcher._fetch_yfinance_news_only(symbol, limit=limit)
            all_news.extend(yf_news)
        except Exception as e:
            logger.error(f"Failed to fetch YF news in aggregator: {e}")

        # Sort by publish time descending
        all_news.sort(key=lambda x: x.get("providerPublishTime", 0), reverse=True)
        
        # Deduplicate by title
        seen_titles = set()
        deduped = []
        for n in all_news:
            t = n['title'].strip().lower()
            if t not in seen_titles:
                seen_titles.add(t)
                deduped.append(n)
                
        # If we couldn't find symbol-specific news in RSS, fallback to general news
        if not deduped:
            mc_gen = cls.fetch_rss_feed(cls.RSS_FEEDS["moneycontrol_buzzing"], "Moneycontrol", None)
            et_gen = cls.fetch_rss_feed(cls.RSS_FEEDS["economic_times"], "Economic Times", None)
            gen_news = mc_gen + et_gen
            gen_news.sort(key=lambda x: x.get("providerPublishTime", 0), reverse=True)
            return gen_news[:limit]

        return deduped[:limit]
