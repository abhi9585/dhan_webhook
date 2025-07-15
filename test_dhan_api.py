import requests

DHAN_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzUyNjY3MzY2LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwNzczNTIwNCJ9.e4E4_h8W39nc8nZUN1d1594jC-AdDH4-b6LeV3pa4J0xJSPaa-qMH-seJ_BkqkaNVFRZ0T0fN5fqTr44hnddqw"

url = "https://api.dhan.co/market-feed/quote/NSE_INDEX/NIFTY_BANK"

headers = {
    "access-token": DHAN_TOKEN
}

print("➡ Requesting:", url)
response = requests.get(url, headers=headers)

print("🌐 Status Code:", response.status_code)
print("📄 Raw Text:", response.text)

try:
    print("🧾 Parsed JSON:", response.json())
except Exception as e:
    print("❌ JSON Parse Error:", e)