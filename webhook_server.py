# webhook_server.py
import os
import json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Load env vars
CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN")

# Dhan API Endpoint
ORDER_API_URL = "https://api.dhan.co/orders"

@app.route('/webhook', methods=['POST'])
def webhook():
    # Verify webhook token
    token = request.args.get('token')
    if token != WEBHOOK_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    print("🔔 Incoming Webhook:", data)

    try:
        signal = data.get("signal")
        if signal not in ["buy_ce", "buy_pe"]:
            return jsonify({"error": "Invalid signal"}), 400

        trading_symbol = "BANKNIFTY25JUL47000CE" if signal == "buy_ce" else "BANKNIFTY25JUL47000PE"
        order_payload = {
            "transactionType": "BUY",
            "orderType": "MARKET",
            "exchange": "NSE",
            "securityId": trading_symbol,
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

        response = requests.post(ORDER_API_URL, headers=headers, json=order_payload)
        print("✅ Order Response:", response.text)
        return jsonify({"message": "Order placed", "response": response.json()})

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
