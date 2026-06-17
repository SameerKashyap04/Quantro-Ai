-- ============================================================
-- Quantro Personal AI — Seed Data
-- ============================================================
-- NSE Stock Universe: NIFTY 50, NIFTY Next 50, Key ETFs, Indices
-- ============================================================

-- ── Indices ──────────────────────────────────────────────────
INSERT INTO stocks (symbol, name, sector, exchange, is_index, yfinance_symbol) VALUES
    ('NIFTY', 'NIFTY 50 Index', 'Index', 'NSE', true, '^NSEI'),
    ('BANKNIFTY', 'NIFTY Bank Index', 'Index', 'NSE', true, '^NSEBANK'),
    ('FINNIFTY', 'NIFTY Financial Services Index', 'Index', 'NSE', true, 'NIFTY_FIN_SERVICE.NS'),
    ('MIDCAP', 'NIFTY Midcap 50 Index', 'Index', 'NSE', true, '^NSEMDCP50')
ON CONFLICT (symbol) DO NOTHING;

-- ── ETFs ─────────────────────────────────────────────────────
INSERT INTO stocks (symbol, name, sector, exchange, is_etf, yfinance_symbol) VALUES
    ('NIFTYBEES', 'Nippon India ETF Nifty BeES', 'ETF', 'NSE', true, 'NIFTYBEES.NS'),
    ('BANKBEES', 'Nippon India ETF Bank BeES', 'ETF', 'NSE', true, 'BANKBEES.NS'),
    ('GOLDBEES', 'Nippon India ETF Gold BeES', 'ETF', 'NSE', true, 'GOLDBEES.NS'),
    ('JUNIORBEES', 'Nippon India ETF Junior BeES', 'ETF', 'NSE', true, 'JUNIORBEES.NS')
ON CONFLICT (symbol) DO NOTHING;

-- ── NIFTY 50 Stocks ──────────────────────────────────────────
INSERT INTO stocks (symbol, name, sector, market_cap_category, exchange, yfinance_symbol) VALUES
    ('RELIANCE', 'Reliance Industries Ltd', 'Energy', 'largecap', 'NSE', 'RELIANCE.NS'),
    ('TCS', 'Tata Consultancy Services Ltd', 'IT', 'largecap', 'NSE', 'TCS.NS'),
    ('HDFCBANK', 'HDFC Bank Ltd', 'Banking', 'largecap', 'NSE', 'HDFCBANK.NS'),
    ('INFY', 'Infosys Ltd', 'IT', 'largecap', 'NSE', 'INFY.NS'),
    ('ICICIBANK', 'ICICI Bank Ltd', 'Banking', 'largecap', 'NSE', 'ICICIBANK.NS'),
    ('HINDUNILVR', 'Hindustan Unilever Ltd', 'FMCG', 'largecap', 'NSE', 'HINDUNILVR.NS'),
    ('ITC', 'ITC Ltd', 'FMCG', 'largecap', 'NSE', 'ITC.NS'),
    ('SBIN', 'State Bank of India', 'Banking', 'largecap', 'NSE', 'SBIN.NS'),
    ('BHARTIARTL', 'Bharti Airtel Ltd', 'Telecom', 'largecap', 'NSE', 'BHARTIARTL.NS'),
    ('KOTAKBANK', 'Kotak Mahindra Bank Ltd', 'Banking', 'largecap', 'NSE', 'KOTAKBANK.NS'),
    ('LT', 'Larsen & Toubro Ltd', 'Infrastructure', 'largecap', 'NSE', 'LT.NS'),
    ('AXISBANK', 'Axis Bank Ltd', 'Banking', 'largecap', 'NSE', 'AXISBANK.NS'),
    ('BAJFINANCE', 'Bajaj Finance Ltd', 'Financial Services', 'largecap', 'NSE', 'BAJFINANCE.NS'),
    ('ASIANPAINT', 'Asian Paints Ltd', 'Consumer Durables', 'largecap', 'NSE', 'ASIANPAINT.NS'),
    ('MARUTI', 'Maruti Suzuki India Ltd', 'Automobile', 'largecap', 'NSE', 'MARUTI.NS'),
    ('SUNPHARMA', 'Sun Pharmaceutical Industries Ltd', 'Pharma', 'largecap', 'NSE', 'SUNPHARMA.NS'),
    ('TATAMOTORS', 'Tata Motors Ltd', 'Automobile', 'largecap', 'NSE', 'TATAMOTORS.NS'),
    ('TITAN', 'Titan Company Ltd', 'Consumer Durables', 'largecap', 'NSE', 'TITAN.NS'),
    ('WIPRO', 'Wipro Ltd', 'IT', 'largecap', 'NSE', 'WIPRO.NS'),
    ('ULTRACEMCO', 'UltraTech Cement Ltd', 'Cement', 'largecap', 'NSE', 'ULTRACEMCO.NS'),
    ('HCLTECH', 'HCL Technologies Ltd', 'IT', 'largecap', 'NSE', 'HCLTECH.NS'),
    ('NESTLEIND', 'Nestle India Ltd', 'FMCG', 'largecap', 'NSE', 'NESTLEIND.NS'),
    ('BAJAJFINSV', 'Bajaj Finserv Ltd', 'Financial Services', 'largecap', 'NSE', 'BAJAJFINSV.NS'),
    ('POWERGRID', 'Power Grid Corp of India Ltd', 'Power', 'largecap', 'NSE', 'POWERGRID.NS'),
    ('NTPC', 'NTPC Ltd', 'Power', 'largecap', 'NSE', 'NTPC.NS'),
    ('TATASTEEL', 'Tata Steel Ltd', 'Metals', 'largecap', 'NSE', 'TATASTEEL.NS'),
    ('ONGC', 'Oil & Natural Gas Corp Ltd', 'Energy', 'largecap', 'NSE', 'ONGC.NS'),
    ('ADANIENT', 'Adani Enterprises Ltd', 'Diversified', 'largecap', 'NSE', 'ADANIENT.NS'),
    ('ADANIPORTS', 'Adani Ports & SEZ Ltd', 'Infrastructure', 'largecap', 'NSE', 'ADANIPORTS.NS'),
    ('TECHM', 'Tech Mahindra Ltd', 'IT', 'largecap', 'NSE', 'TECHM.NS'),
    ('JSWSTEEL', 'JSW Steel Ltd', 'Metals', 'largecap', 'NSE', 'JSWSTEEL.NS'),
    ('COALINDIA', 'Coal India Ltd', 'Mining', 'largecap', 'NSE', 'COALINDIA.NS'),
    ('HDFCLIFE', 'HDFC Life Insurance Co Ltd', 'Insurance', 'largecap', 'NSE', 'HDFCLIFE.NS'),
    ('SBILIFE', 'SBI Life Insurance Co Ltd', 'Insurance', 'largecap', 'NSE', 'SBILIFE.NS'),
    ('GRASIM', 'Grasim Industries Ltd', 'Cement', 'largecap', 'NSE', 'GRASIM.NS'),
    ('M&M', 'Mahindra & Mahindra Ltd', 'Automobile', 'largecap', 'NSE', 'M&M.NS'),
    ('BAJAJ-AUTO', 'Bajaj Auto Ltd', 'Automobile', 'largecap', 'NSE', 'BAJAJ-AUTO.NS'),
    ('DRREDDY', 'Dr Reddys Laboratories Ltd', 'Pharma', 'largecap', 'NSE', 'DRREDDY.NS'),
    ('CIPLA', 'Cipla Ltd', 'Pharma', 'largecap', 'NSE', 'CIPLA.NS'),
    ('DIVISLAB', 'Divis Laboratories Ltd', 'Pharma', 'largecap', 'NSE', 'DIVISLAB.NS'),
    ('EICHERMOT', 'Eicher Motors Ltd', 'Automobile', 'largecap', 'NSE', 'EICHERMOT.NS'),
    ('INDUSINDBK', 'IndusInd Bank Ltd', 'Banking', 'largecap', 'NSE', 'INDUSINDBK.NS'),
    ('APOLLOHOSP', 'Apollo Hospitals Enterprise Ltd', 'Healthcare', 'largecap', 'NSE', 'APOLLOHOSP.NS'),
    ('TATACONSUM', 'Tata Consumer Products Ltd', 'FMCG', 'largecap', 'NSE', 'TATACONSUM.NS'),
    ('BPCL', 'Bharat Petroleum Corp Ltd', 'Energy', 'largecap', 'NSE', 'BPCL.NS'),
    ('BRITANNIA', 'Britannia Industries Ltd', 'FMCG', 'largecap', 'NSE', 'BRITANNIA.NS'),
    ('HEROMOTOCO', 'Hero MotoCorp Ltd', 'Automobile', 'largecap', 'NSE', 'HEROMOTOCO.NS'),
    ('HINDALCO', 'Hindalco Industries Ltd', 'Metals', 'largecap', 'NSE', 'HINDALCO.NS'),
    ('LTIM', 'LTIMindtree Ltd', 'IT', 'largecap', 'NSE', 'LTIM.NS'),
    ('SHRIRAMFIN', 'Shriram Finance Ltd', 'Financial Services', 'largecap', 'NSE', 'SHRIRAMFIN.NS')
ON CONFLICT (symbol) DO NOTHING;

-- ── NIFTY Next 50 Stocks (selected) ─────────────────────────
INSERT INTO stocks (symbol, name, sector, market_cap_category, exchange, yfinance_symbol) VALUES
    ('HAVELLS', 'Havells India Ltd', 'Consumer Durables', 'largecap', 'NSE', 'HAVELLS.NS'),
    ('PIDILITIND', 'Pidilite Industries Ltd', 'Chemicals', 'largecap', 'NSE', 'PIDILITIND.NS'),
    ('SIEMENS', 'Siemens Ltd', 'Capital Goods', 'largecap', 'NSE', 'SIEMENS.NS'),
    ('GODREJCP', 'Godrej Consumer Products Ltd', 'FMCG', 'largecap', 'NSE', 'GODREJCP.NS'),
    ('DLF', 'DLF Ltd', 'Real Estate', 'largecap', 'NSE', 'DLF.NS'),
    ('ABB', 'ABB India Ltd', 'Capital Goods', 'largecap', 'NSE', 'ABB.NS'),
    ('AMBUJACEM', 'Ambuja Cements Ltd', 'Cement', 'largecap', 'NSE', 'AMBUJACEM.NS'),
    ('VEDL', 'Vedanta Ltd', 'Metals', 'largecap', 'NSE', 'VEDL.NS'),
    ('TRENT', 'Trent Ltd', 'Retail', 'largecap', 'NSE', 'TRENT.NS'),
    ('ZOMATO', 'Zomato Ltd', 'Internet', 'largecap', 'NSE', 'ZOMATO.NS'),
    ('JIOFIN', 'Jio Financial Services Ltd', 'Financial Services', 'largecap', 'NSE', 'JIOFIN.NS'),
    ('IRCTC', 'Indian Railway Catering & Tourism Corp Ltd', 'Tourism', 'largecap', 'NSE', 'IRCTC.NS'),
    ('HAL', 'Hindustan Aeronautics Ltd', 'Defence', 'largecap', 'NSE', 'HAL.NS'),
    ('IOC', 'Indian Oil Corp Ltd', 'Energy', 'largecap', 'NSE', 'IOC.NS'),
    ('BANKBARODA', 'Bank of Baroda', 'Banking', 'largecap', 'NSE', 'BANKBARODA.NS'),
    ('PNB', 'Punjab National Bank', 'Banking', 'largecap', 'NSE', 'PNB.NS'),
    ('TATAPOWER', 'Tata Power Company Ltd', 'Power', 'largecap', 'NSE', 'TATAPOWER.NS'),
    ('CANBK', 'Canara Bank', 'Banking', 'largecap', 'NSE', 'CANBK.NS'),
    ('NAUKRI', 'Info Edge (India) Ltd', 'Internet', 'largecap', 'NSE', 'NAUKRI.NS'),
    ('ICICIPRULI', 'ICICI Prudential Life Insurance Co Ltd', 'Insurance', 'largecap', 'NSE', 'ICICIPRULI.NS')
ON CONFLICT (symbol) DO NOTHING;
