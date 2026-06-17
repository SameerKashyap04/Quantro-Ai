import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
}

try:
    session = requests.Session()
    session.headers.update(headers)
    # Ping main page to get cookies
    session.get("https://www.nseindia.com", timeout=5)
    
    # Get top gainers for NIFTY 50 (index=nifty)
    res = session.get("https://www.nseindia.com/api/live-analysis-variations?index=gainers", timeout=5)
    print("Gainers API Status:", res.status_code)
    
    if res.status_code == 200:
        data = res.json()
        print("Got gainers data:", list(data.keys()))
        if 'NIFTY' in data:
            symbols = [item['symbol'] for item in data['NIFTY']['data'][:5]]
            print("Top Nifty Gainers:", symbols)
except Exception as e:
    print("Error:", e)
