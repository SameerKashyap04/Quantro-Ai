import requests

tv_payload = {
    "filter": [
        {"left": "exchange", "operation": "equal", "right": "NSE"},
        {"left": "market_cap_basic", "operation": "egreater", "right": 50000000000}, # 5000 Cr
        {"left": "volume", "operation": "egreater", "right": 1000000} # 1M volume
    ],
    "options": {"lang": "en"},
    "markets": ["india"],
    "symbols": {"query": {"types": []}, "tickers": []},
    "columns": ["name", "close", "change"],
    "sort": {"sortBy": "change", "sortOrder": "desc"},
    "range": [0, 15]
}
res = requests.post("https://scanner.tradingview.com/india/scan", json=tv_payload, headers={'User-Agent': 'Mozilla/5.0'})
print("TV Gainers:", [x['d'][0] for x in res.json().get('data', [])])
