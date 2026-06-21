import pandas as pd
import logging
from typing import Optional
from tvDatafeed import TvDatafeed, Interval
import feedparser
import requests
import random
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize tvDatafeed (anonymous mode)
try:
    tv = TvDatafeed()
except Exception as e:
    logger.error(f"Failed to initialize tvDatafeed: {e}")
    tv = None

class TradingViewFetcher:
    """Fetches market data from TradingView and Google News for portfolio analysis."""

    @staticmethod
    def _clean_symbol(symbol: str, is_index: bool = False) -> str:
        """Clean symbol for TradingView (remove .NS, etc)"""
        clean_sym = symbol.replace(".NS", "").replace(".BO", "")
        # Handle special indices if needed
        if is_index:
            if clean_sym == "NIFTY_50":
                return "NIFTY"
            if clean_sym == "NIFTY_BANK":
                return "BANKNIFTY"
        return clean_sym

    @staticmethod
    def fetch_ohlcv(symbol: str, period: str = "1mo", interval: str = "1d", is_index: bool = False) -> pd.DataFrame:
        """Fetch OHLCV data using tvDatafeed."""
        if tv is None:
            return pd.DataFrame()
            
        tv_sym = TradingViewFetcher._clean_symbol(symbol, is_index)
        exchange = "NSE"
        
        try:
            # Map interval string to tvDatafeed Interval
            tv_interval = Interval.in_daily
            if interval == "1wk":
                tv_interval = Interval.in_weekly
            elif interval == "1mo":
                tv_interval = Interval.in_monthly
            elif interval == "1h":
                tv_interval = Interval.in_1_hour
            elif interval in ["15m", "30m", "5m"]:
                # Map other intervals if needed, defaulting to daily for backtests
                pass
                
            # Estimate n_bars from period
            n_bars = 100
            if "mo" in period:
                n_bars = int(period.replace("mo", "")) * 22
            elif "y" in period:
                n_bars = int(period.replace("y", "")) * 252
            elif "d" in period:
                n_bars = int(period.replace("d", ""))

            df = tv.get_hist(symbol=tv_sym, exchange=exchange, interval=tv_interval, n_bars=n_bars)
            
            if df is None or df.empty:
                logger.warning(f"No data returned from TradingView for {tv_sym}")
                return pd.DataFrame()

            # Reset index to get datetime column
            df.reset_index(inplace=True)
            
            # Rename columns to match what the strategy expects
            df.columns = [str(col).lower() for col in df.columns]
            
            if "datetime" in df.columns:
                df.rename(columns={"datetime": "timestamp"}, inplace=True)
            elif "date" in df.columns:
                df.rename(columns={"date": "timestamp"}, inplace=True)
                
            # Return standard columns
            cols = ["timestamp", "open", "high", "low", "close", "volume"]
            # Ensure all columns exist
            for c in cols:
                if c not in df.columns:
                    df[c] = 0
                    
            return df[cols]
            
        except Exception as e:
            logger.error(f"Error fetching TradingView data for {tv_sym}: {e}")
            return pd.DataFrame()

    @staticmethod
    def fetch_latest_price(symbol: str, is_index: bool = False) -> Optional[dict]:
        """Fetch the current/latest price using tvDatafeed (n_bars=2)."""
        if tv is None:
            return None
            
        tv_sym = TradingViewFetcher._clean_symbol(symbol, is_index)
        
        try:
            df = tv.get_hist(symbol=tv_sym, exchange="NSE", interval=Interval.in_daily, n_bars=2)
            if df is None or df.empty:
                return None
                
            current_price = float(df['close'].iloc[-1])
            prev_close = float(df['close'].iloc[-2]) if len(df) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0
            
            return {
                "symbol": symbol,
                "price": current_price,
                "change": change,
                "change_pct": change_pct,
                "volume": float(df['volume'].iloc[-1]) if 'volume' in df.columns else 0,
            }
        except Exception as e:
            logger.error(f"Error fetching latest price from TradingView for {tv_sym}: {e}")
            return None

    @staticmethod
    def fetch_fundamentals(symbol: str, is_index: bool = False) -> dict:
        """Return empty fundamentals as TradingView does not provide them for free without web scraping."""
        return {}

    @staticmethod
    def fetch_news(symbol: str, is_index: bool = False, limit: int = 5) -> list[dict]:
        """Fetch news using Google News RSS."""
        clean_sym = TradingViewFetcher._clean_symbol(symbol, is_index)
        query = f"{clean_sym} share price NSE India"
        url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}"
        
        try:
            feed = feedparser.parse(url)
            results = []
            for entry in feed.entries[:limit]:
                # Convert pubDate to timestamp if possible
                pub_time = 0
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    from time import mktime
                    pub_time = int(mktime(entry.published_parsed))
                    
                results.append({
                    "title": entry.title,
                    "publisher": entry.source.title if hasattr(entry, 'source') else "Google News",
                    "link": entry.link,
                    "providerPublishTime": pub_time
                })
            return results
        except Exception as e:
            logger.error(f"Error fetching Google News for {clean_sym}: {e}")
            return []
