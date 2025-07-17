from flask import Flask, request, jsonify
import requests
import os
import traceback
from datetime import datetime
from waitress import serve

app = Flask(_name_)
print("Webhook server started")

# === Configuration ===
DHAN_BASE = "https://api.dhan.co"
DHAN_TOKEN = os.getenv("DHAN_TOKEN")

# === Get Bank Nifty Spot Price ===
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

        print("➡ Requesting spot with:", payload)
        response = requests.post(url, headers=headers, json=payload)

        print("🌐 Status Code:", response.status_code)
        print("📄 Raw Response:", response.text)

        if response.status_code != 200:
            return 0

        data = response.json()
        ltp = float(data.get("data", {}).get("last_traded_price", 0))
        print("✅ LTP fetched:", ltp)
        return round(ltp / 100) * 100

    except Exception as e:
        print("❌ Error fetching spot:", e)
        return 0

# === Webhook Route ===
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Webhook ping received at {now}", flush=True)

        if request.method == "GET":
            return jsonify({"status": "ok", "message": "GET received"})

        data = request.json
        direction = data.get("direction", "").upper()
        option_type = data.get("option_type", "").upper()
        expiry = data.get("expiry", datetime.today().strftime("%y%m%d"))
        quantity = 30  # Fixed 1 lot

        if not all([direction, option_type]):
            return jsonify({"status": "error", "message": "Missing required fields"})

        # === Get ATM strike price ===
        spot_strike = get_banknifty_spot()
        if spot_strike == 0:
            return jsonify({"status": "error", "message": "Failed to fetch spot"})

        # === Build option symbol ===
        symbol = f"BANKNIFTY{expiry}{spot_strike}{option_type}"
        dhan_symbol = f"NSE:{symbol}"

        # === Order Payload ===
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

        # === Send Order ===
        response = requests.post(f"{DHAN_BASE}/orders", json=payload, headers=headers)

        return jsonify({
            "status": "success",
            "symbol": dhan_symbol,
            "response": response.json()
        })

    except Exception as e:
        return jsonify({"status": "error", "trace": traceback.format_exc()})

# === Start Waitress Server ===
if _name_ == "_main_":
    print("Webhook server starting with Waitress...")
    serve(app, host="0.0.0.0", port=10000)
