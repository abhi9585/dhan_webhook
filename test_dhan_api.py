import requests
import os

# Load DHAN token from environment
DHAN_TOKEN = os.getenv("DHAN_TOKEN")
DHAN_BASE = "https://api.dhan.co"

def get_banknifty_spot():
    url = f"{DHAN_BASE}/market-feed/quotes"
    headers = {
        "access-token": DHAN_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "security_id": "NSE_INDEX|26009"
    }

    print("➡ Sending request to Dhan for BankNifty Spot...")
    response = requests.post(url, headers=headers, json=payload)
    
    print("🌐 Status Code:", response.status_code)
    print("📄 Response Text:", response.text)

    if response.status_code == 200:
        data = response.json()
        ltp = data.get("data", {}).get("last_traded_price", None)
        if ltp:
            print("✅ BankNifty Spot Price:", ltp)
        else:
            print("⚠ Price not found in response.")
    else:
        print("❌ Failed to fetch spot price.")

if _name_ == "_main_":
    get_banknifty_spot()
