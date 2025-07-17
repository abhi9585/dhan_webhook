import requests
import os
from datetime import datetime

# === Configuration ===
DHAN_BASE = "https://api.dhan.co"
DHAN_TOKEN = os.getenv("DHAN_TOKEN")  # make sure this is set in Render

def get_banknifty_spot():
    url = f"{DHAN_BASE}/market-feed/quotes"
    headers = {
        "access-token": DHAN_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "security_id": "NSE_INDEX|26009"
    }

    print("Requesting BankNifty spot...")
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print("Failed to fetch spot")
        return 0

    data = response.json()
    ltp = float(data.get("data", {}).get("last_traded_price", 0))
    print("LTP fetched:", ltp)
    return round(ltp / 100) * 100

def test_direct_order():
    spot_strike = get_banknifty_spot()
    if spot_strike == 0:
        print("❌ Error: Could not get spot")
        return

    expiry = datetime.today().strftime("%y%m%d")  # change this if you want fixed expiry
    symbol = f"BANKNIFTY{expiry}{spot_strike}CE"
    dhan_symbol = f"NSE:{symbol}"

    payload = {
        "transaction_type": "BUY",
        "symbol": dhan_symbol,
        "exchange_segment": "NSE_OPTIDX",
        "order_type": "MARKET",
        "product": "INTRADAY",
        "quantity": 30,
        "price": 0,
        "trigger_price": 0,
        "validity": "DAY"
    }

    headers = {
        "access-token": DHAN_TOKEN,
        "Content-Type": "application/json"
    }

    print("Placing order for:", dhan_symbol)
    response = requests.post(f"{DHAN_BASE}/orders", json=payload, headers=headers)

    print("Status:", response.status_code)
    print("Response:", response.text)

if _name_ == "_main_":
    test_direct_order()
