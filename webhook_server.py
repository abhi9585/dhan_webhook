from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)
print("✅ Webhook server started")

DHAN_BASE = "https://api.dhan.co"
DHAN_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzUyNjY3MzY2LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwNzczNTIwNCJ9.e4E4_h8W39nc8nZUN1d1594jC-AdDH4-b6LeV3pa4J0xJSPaa-qMH-seJ_BkqkaNVFRZ0T0fN5fqTr44hnddqw"

def get_banknifty_spot():
    try:
        url = f"{DHAN_BASE}/market-feed/quotes"
        headers = {
            "access-token": DHAN_TOKEN,
            "Content-Type": "application/json"
        }

        payload = {
            "security_id": "NSE_INDEX|26009"
        }

        print("➡ Sending POST request to fetch BankNifty spot...")
        response = requests.post(url, headers=headers, json=payload)
        print("🌐 Status Code:", response.status_code)
        print("📄 Response Text:", response.text)

        if response.status_code != 200:
            return 0

        data = response.json()
        ltp = float(data.get("data", {}).get("last_traded_price", 0))
        print("✅ Fetched LTP:", ltp)
        return round(ltp / 100) * 100

    except Exception as e:
        print("❌ Exception while fetching spot:", e)
        return 0

        data = response.json()
        ltp = float(data.get("data", {}).get("last_traded_price", 0))
        print("✅ Fetched LTP:", ltp)
        return round(ltp / 100) * 100

    except Exception as e:
        print("❌ Exception while fetching spot:", e)
        print("📛 Spot fetch failed — response.text:", response.text)
        return 0

        data = response.json()
        ltp = float(data.get("data", {}).get("last_traded_price", 0))
        print("✅ Got LTP:", ltp)
        return round(ltp / 100) * 100

    except Exception as e:
        print("❌ Spot Fetch Error:", e)
        return 0

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"📩 Webhook received at {now}")

        if request.method == "GET":
            return jsonify({"status": "ok", "message": "GET received"})

        data = request.json
        direction = data.get("direction", "").upper()
        option_type = data.get("option_type", "").upper()
        expiry = data.get("expiry", datetime.today().strftime("%y%m%d"))
        quantity = 30

        if not all([direction, option_type]):
            return jsonify({"status": "error", "message": "Missing required fields"})

        spot_strike = get_banknifty_spot()
        if spot_strike == 0:
            return jsonify({"status": "error", "message": "Failed to fetch spot"})

        symbol = f"BANKNIFTY{expiry}{spot_strike}{option_type}"
        dhan_symbol = f"NSE:{symbol}"

        payload = {
            "transaction_type": direction,
            "symbol": dhan_symbol,
            "exchange_segment": "NSE_OPTIDX",
            "order_type": "MARKET",
            "product": "INTRADAY",
            "quantity": quantity,
            "price": 0,
            "trigger_price": 0,
            "validity": "DAY"
        }

        headers = {
            "access-token": DHAN_TOKEN,
            "Content-Type": "application/json"
        }

        response = requests.post(f"{DHAN_BASE}/orders", json=payload, headers=headers)

        return jsonify({
            "status": "success",
            "symbol": dhan_symbol,
            "response": response.json()
        })

    except Exception as e:
        return jsonify({"status": "error", "trace": str(e)})

from waitress import serve

if __name__ == "__main__":
    print("🚀 Starting Webhook server on port 10000...")
    serve(app, host="0.0.0.0", port=10000)
