import pandas as pd

# Create a dummy Groww-like excel file
df_dummy = pd.DataFrame({
    'Instrument': ['TCS', 'RELIANCE'],
    'Quantity': [10, 5],
    'Avg. Price': [3500.0, 2500.0],
    'LTP': [3600.0, 2600.0]
})
df_dummy.to_excel("dummy.xlsx", index=False)

# Read it back exactly as the service does
df = pd.read_excel("dummy.xlsx", header=0)
df.columns = df.columns.astype(str).str.strip().str.lower()
print("Columns:", df.columns.tolist())

symbol_col = next((c for c in df.columns if any(x in c for x in ['instrument', 'symbol', 'stock', 'company', 'name', 'asset', 'fund'])), None)
qty_col = next((c for c in df.columns if any(x in c for x in ['qty', 'quantity', 'shares', 'balance', 'available', 'units'])), None)

print(f"Symbol Col: {symbol_col}, Qty Col: {qty_col}")

upserted_count = 0
for _, row in df.iterrows():
    symbol = str(row[symbol_col]).strip().upper()
    if not symbol or symbol == 'NAN':
        continue
    try:
        qty = int(row[qty_col])
        if qty <= 0:
            continue
    except (ValueError, TypeError):
        print(f"Failed qty: {row[qty_col]}")
        continue
    upserted_count += 1
    
print(f"Upserted: {upserted_count}")

