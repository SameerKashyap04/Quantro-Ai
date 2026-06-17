"""
Quantro Personal AI — NLP Sentiment Analyzer
"""
import re

class SentimentAnalyzer:
    """Lightweight heuristic-based sentiment analyzer for financial news."""

    BULLISH_KEYWORDS = [
        "surge", "jump", "soar", "gain", "profit", "beat", "up", "high",
        "buy", "upgrade", "outperform", "bull", "growth", "dividend",
        "partnership", "acquire", "launch", "record", "rally", "positive",
        "strong", "raise", "breakout"
    ]

    BEARISH_KEYWORDS = [
        "plunge", "drop", "fall", "loss", "miss", "down", "low", "sell",
        "downgrade", "underperform", "bear", "decline", "cut", "lawsuit",
        "investigation", "debt", "bankrupt", "crash", "negative", "weak",
        "slump", "misses"
    ]

    @classmethod
    def analyze_headlines(cls, headlines: list[str]) -> float:
        """
        Analyze a list of headlines and return a net sentiment score between -1.0 and 1.0.
        > 0 is bullish, < 0 is bearish.
        """
        if not headlines:
            return 0.0

        total_score = 0.0
        
        for headline in headlines:
            words = re.findall(r'\b\w+\b', headline.lower())
            
            bull_count = sum(1 for w in words if w in cls.BULLISH_KEYWORDS)
            bear_count = sum(1 for w in words if w in cls.BEARISH_KEYWORDS)
            
            # Simple net score per headline
            if bull_count > bear_count:
                total_score += 1.0
            elif bear_count > bull_count:
                total_score -= 1.0
                
        # Normalize between -1.0 and 1.0
        normalized_score = total_score / len(headlines)
        return normalized_score
