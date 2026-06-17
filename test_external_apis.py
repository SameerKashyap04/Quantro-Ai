import requests
headers = {'User-Agent': 'Mozilla/5.0'}

# 1. TradingView
try:
    tv_payload = {"filter":[{"left":"change","operation":"nempty"}],"options":{"lang":"en"},"markets":["india"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["name","close","change","volume","Recommend.All"],"sort":{"sortBy":"change","sortOrder":"desc"},"range":[0,10]}
    tv_res = requests.post("https://scanner.tradingview.com/india/scan", json=tv_payload, headers=headers)
    print("TradingView:", [x['d'][0] for x in tv_res.json().get('data', [])])
except Exception as e:
    print("TV Error:", e)

# 2. Groww API
try:
    # Top gainers API usually: https://groww.in/v1/api/stocks_data/v1/tr_live/top_gainers?discovery_filter_types=TOP_GAINERS
    groww_res = requests.get("https://groww.in/v1/api/stocks_data/v1/tr_live/top_gainers", headers=headers)
    if groww_res.status_code == 200:
        print("Groww:", [x.get('symbol') for x in groww_res.json()])
    else:
        print("Groww Status:", groww_res.status_code)
except Exception as e:
    print("Groww Error:", e)

