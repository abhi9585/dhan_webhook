from flask import Flask, request, jsonify
import os
from datetime import datetime
import traceback
import requests

app = Flask(_name_)
print("Webhook server started")

DHAN_BASE = "https://api.dhan.co"
DHAN_TOKEN = os.getenv("DHAN_TOKEN")

def get_banknifty_spot():
    try:
        url = f"{DHAN_BASE}/market-feed/quote/NSE_INDEX/Nifty Bank"
        headers = {"access-token": DHAN_TOKEN}
        res = requests.get(url, headers=headers)
        data = res.json()
        ltp = float(data.get("dhan", {}).get("ltp", 0))
        return round(ltp / 100) * 100
    except Exception as e:
        print("Error fetching spot price:", e)
        return 0

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Webhook ping received at {now}", flush=True)

        if request.method == "GET":
            return jsonify({"status": "ok", "message": "GET received"})

        data = request.json

        direction = data.get("direction", "").upper()
        option_type = data.get("option_type", "").upper()
        expiry = data.get("expiry", "")
        quantity = 30

        if not all([direction, option_type, expiry]):
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
        return jsonify({"status": "error", "trace": traceback.format_exc()})


# === Keep the server alive using Waitress ===
from waitress import serve

if _name_ == "_main_":
    print("Webhook server starting with Waitress...")
    serve(app, host="0.0.0.0", port=10000)