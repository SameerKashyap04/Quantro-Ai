import yfinance as yf
from packages.shared.nse_universe import NIFTY_50, NIFTY_NEXT_50
universe = NIFTY_50 + NIFTY_NEXT_50
tickers = [f"{s}.NS" for s in universe]
data = yf.download(tickers, period="1d", group_by="ticker", progress=False, threads=True)

performances = []
for t in tickers:
    try:
        if t in data.columns.levels[0]:
            df = data[t]
        else:
            df = data
        if not df.empty and len(df) > 0:
            open_p = df['Open'].iloc[-1]
            close_p = df['Close'].iloc[-1]
            if open_p > 0:
                pct = ((close_p - open_p) / open_p) * 100
                performances.append((t, pct))
    except Exception as e:
        print(f"Error {t}: {e}")

performances.sort(key=lambda x: x[1], reverse=True)
print("Top 5:")
print(performances[:5])
