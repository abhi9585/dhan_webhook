import os
import json
import csv
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# === Load environment variables ===
CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN")
print(f"🔐 Server-side token from env: {WEBHOOK_TOKEN}")
CSV_FILE = "api-scrip-master.csv"  # Must be in same folder or update full path

# === Constants ===
EXPIRY_TEXT = "Jul2025"
UNDERLYING_ID = "26009"
ORDER_API_URL = "https://api.dhan.co/orders"

# === Find instrument token ===
def find_instrument_token(strike: str, option_type: str):
    symbol = f"BANKNIFTY-{EXPIRY_TEXT}-{strike}-{option_type}"
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if (
                row.get("SYMBOL_NAME") == symbol and
                row.get("UNDERLYING_SECURITY_ID") == UNDERLYING_ID
            ):
                return row.get("DISPLAY_NAME")
    return None

@app.route('/webhook', methods=['POST'])
def webhook():
    # ✅ Token check
    auth_header = request.headers.get("Authorization")
    expected_header = f"Bearer {WEBHOOK_TOKEN}"

    if auth_header != expected_header:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json
        signal = data.get("signal")
        strike = data.get("strike")

        if signal not in ["buy_ce", "buy_pe"] or not strike:
            return jsonify({"error": "Invalid signal or strike"}), 400

        option_type = "CE" if signal == "buy_ce" else "PE"
        instrument_token = find_instrument_token(strike, option_type)

        if not instrument_token:
            return jsonify({"error": "Instrument token not found"}), 404

        # ✅ Prepare order
        order_payload = {
            "transactionType": "BUY",
            "orderType": "MARKET",
            "exchange": "NSE",
            "exchangeSegment": "NSE_FNO",
            "securityId": 1010000075860795,
            "quantity": 30,
            "price": 0,
            "productType": "INTRADAY",
            "orderValidity": "DAY",
            "disclosedQuantity": 0,
            "afterMarketOrder": False,
            "triggerPrice": 0,
            "smartOrder": False,
        }

        headers = {
            "Content-Type": "application/json",
            "Access-Token": ACCESS_TOKEN,
            "Client-Id": CLIENT_ID
        }
        print("📦 Order Payload:")
        print(json.dumps(order_payload, indent=2))
        print("🧾 Headers:", headers)
        response = requests.post(ORDER_API_URL, headers=headers, json=order_payload)
        print("✅ Order Response:", response.text)
        return jsonify({"message": "Order placed", "response": response.json()})

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

# === Run the server ===
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
