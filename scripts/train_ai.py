import asyncio
import sys
import os
import yfinance as yf
import pandas as pd

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from apps.api.database import async_session_factory
from packages.indicators.calculator import IndicatorCalculator
from services.ai_engine.models import AIModelManager
from services.ai_engine.trainer import ModelTrainer

async def fetch_stock_symbols():
    async with async_session_factory() as session:
        result = await session.execute(text("SELECT symbol FROM stocks WHERE is_index = false AND is_etf = false AND is_active = true"))
        return [row[0] for row in result.fetchall()]

def fetch_data_from_yfinance(symbol: str) -> pd.DataFrame:
    print(f"Fetching data for {symbol}...")
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5y", interval="1d")
        if df.empty:
            return df
        
        # Lowercase columns for our indicators/features to work correctly
        df.columns = [col.lower() for col in df.columns]
        
        # Keep only required columns
        req_cols = ['open', 'high', 'low', 'close', 'volume']
        df = df[[col for col in req_cols if col in df.columns]]
        
        # Calculate Indicators
        df = IndicatorCalculator.calculate_all(df)
        
        # Add symbol for reference
        df['symbol'] = symbol
        return df
        
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return pd.DataFrame()

async def main():
    print("Starting AI Training Pipeline...")
    symbols = await fetch_stock_symbols()
    if not symbols:
        print("No stocks found in database. Run seed_db.py first.")
        return

    print(f"Found {len(symbols)} stocks. Downloading historical data...")
    all_dataframes = []
    
    # In a production environment we'd use asyncio to fetch concurrently or a celery queue.
    # For now, we fetch sequentially.
    for sym in symbols:
        df = fetch_data_from_yfinance(sym)
        if not df.empty:
            all_dataframes.append(df)
            
    if not all_dataframes:
        print("Failed to download any data.")
        return
        
    print("Concatenating all data...")
    giant_df = pd.concat(all_dataframes)
    
    # Reset index since date is the index right now and we might have duplicates across symbols
    giant_df = giant_df.reset_index(drop=True)
    
    print("Training AI Model...")
    model_manager = AIModelManager(model_dir="/app/data/models")
    trainer = ModelTrainer(model_manager)
    
    try:
        result = trainer.train_model(giant_df, "primary_model")
        print("Training successful!")
        print(f"Model Name: {result['model_name']}")
        print(f"Accuracy: {result['accuracy']:.2f}")
        print(f"Samples Trained: {result['samples']}")
        print(f"Features: {result['features_used']}")
    except Exception as e:
        print(f"Training failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
