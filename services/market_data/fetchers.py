"""
Quantro Personal AI — Market Data Fetchers
Wraps yfinance for retrieving market data.
"""
import yfinance as yf
import pandas as pd
import logging
from typing import Optional
from packages.shared.nse_universe import get_yfinance_symbol

logger = logging.getLogger(__name__)


class YFinanceFetcher:
    """Fetches market data from Yahoo Finance."""

    @staticmethod
    def fetch_ohlcv(symbol: str, period: str = "1mo", interval: str = "1d", is_index: bool = False) -> pd.DataFrame:
        """
        Fetch OHLCV data.
        period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        """
        yf_symbol = get_yfinance_symbol(symbol, is_index)
        try:
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data returned for {yf_symbol}")
                return pd.DataFrame()

            # Reset index so Date/Datetime becomes a column
            df.reset_index(inplace=True)
            
            # Lowercase all columns
            df.columns = [str(col).lower() for col in df.columns]
            
            # Find the date column
            if "date" in df.columns:
                df.rename(columns={"date": "timestamp"}, inplace=True)
            elif "datetime" in df.columns:
                df.rename(columns={"datetime": "timestamp"}, inplace=True)
            
            # Ensure timestamp exists, if not use the first column assuming it's the date
            if "timestamp" not in df.columns and len(df.columns) > 0:
                df.rename(columns={df.columns[0]: "timestamp"}, inplace=True)

            return df[["timestamp", "open", "high", "low", "close", "volume"]]
            
        except Exception as e:
            logger.error(f"Error fetching data for {yf_symbol}: {e}")
            return pd.DataFrame()

    @staticmethod
    def fetch_latest_price(symbol: str, is_index: bool = False) -> Optional[dict]:
        """Fetch the current/latest price."""
        yf_symbol = get_yfinance_symbol(symbol, is_index)
        try:
            ticker = yf.Ticker(yf_symbol)
            fast_info = ticker.fast_info
            
            if not fast_info:
                return None
                
            current_price = fast_info.last_price
            prev_close = fast_info.previous_close
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0
            
            return {
                "symbol": symbol,
                "price": current_price,
                "change": change,
                "change_pct": change_pct,
                "volume": fast_info.last_volume,
            }
        except Exception as e:
            logger.error(f"Error fetching latest price for {yf_symbol}: {e}")
            return None

    @staticmethod
    def fetch_fundamentals(symbol: str, is_index: bool = False) -> dict:
        """Fetch fundamental data like P/E, ROE, Debt/Equity, etc."""
        if is_index:
            return {}
        yf_symbol = get_yfinance_symbol(symbol, False)
        try:
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            if not info:
                return {}
                
            return {
                "trailingPE": info.get("trailingPE"),
                "forwardPE": info.get("forwardPE"),
                "priceToBook": info.get("priceToBook"),
                "returnOnEquity": info.get("returnOnEquity"),
                "debtToEquity": info.get("debtToEquity"),
                "profitMargins": info.get("profitMargins"),
                "revenueGrowth": info.get("revenueGrowth"),
            }
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {yf_symbol}: {e}")
            return {}

    @staticmethod
    def _fetch_yfinance_news_only(symbol: str, is_index: bool = False, limit: int = 5) -> list[dict]:
        """Fetch latest news for a symbol using only Yahoo Finance."""
        yf_symbol = get_yfinance_symbol(symbol, is_index)
        try:
            ticker = yf.Ticker(yf_symbol)
            news = ticker.news
            if not news:
                return []
            
            results = []
            for item in news[:limit]:
                results.append({
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", ""),
                    "link": item.get("link", ""),
                    "providerPublishTime": item.get("providerPublishTime", 0)
                })
            return results
        except Exception as e:
            logger.error(f"Error fetching YF news for {yf_symbol}: {e}")
            return []

    @staticmethod
    def fetch_news(symbol: str, is_index: bool = False, limit: int = 5) -> list[dict]:
        """Fetch latest news from all premium aggregators and Yahoo Finance."""
        from services.market_data.news_aggregator import NewsAggregator
        return NewsAggregator.fetch_all_news(symbol, limit)
