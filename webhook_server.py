import os
import json
from flask import Flask, request, jsonify
import requests
from test_webhook_handler import get_tokens_from_spot

app = Flask(__name__)

# Load environment variables
CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN")

# API endpoint
ORDER_API_URL = "https://api.dhan.co/orders"

@app.route('/webhook', methods=['POST'])
def webhook():
    # Webhook token validation
    token = request.args.get('token')
    if token != WEBHOOK_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json
        print("📩 Incoming Webhook Data:", data)

        action = data.get("signal")  # buy_ce / buy_pe
        spot = int(data.get("spot", 0))
        qty = int(data.get("quantity", 15))  # Default to 15

        if action not in ["buy_ce", "buy_pe"]:
            return jsonify({"error": "Invalid signal"}), 400

        # Detect ATM tokens
        ce_token, pe_token = get_tokens_from_spot(spot)
        token = ce_token if action == "buy_ce" else pe_token

        if token is None:
            return jsonify({"error": "Instrument token not found"}), 404

        order_payload = {
            "transactionType": "BUY",
            "orderType": "MARKET",
            "exchangeSegment": "NFO",
            "productType": "INTRADAY",
            "securityId": token,
            "quantity": qty,
            "price": 0,
            "triggerPrice": 0,
            "orderValidity": "DAY",
            "disclosedQuantity": 0,
            "afterMarketOrder": False,
            "amoTime": "OPEN",
            "trailingStopLoss": 0,
            "stopLoss": 0,
            "takeProfit": 0
        }

        headers = {
            "Content-Type": "application/json",
            "Access-Token": ACCESS_TOKEN,
            "Client-Id": CLIENT_ID
        }

        response = requests.post(ORDER_API_URL, headers=headers, json=order_payload)
        print("✅ Order Response:", response.status_code, response.text)

        if response.status_code == 200:
            return jsonify({"message": "Order placed"}), 200
        else:
            return jsonify({"error": response.text}), 500

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
