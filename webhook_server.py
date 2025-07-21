from flask import Flask, request, jsonify
import requests
from test_webhook_handler import get_tokens_from_spot  # fetch CE/PE tokens from CSV
import os

app = Flask(__name__)

# === Read credentials from environment variables ===
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

# === Dhan API URL ===
PLACE_ORDER_URL = "https://api.dhan.co/orders"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("📥 Incoming Webhook Data:", data)

        # Extract data from webhook
        spot_price = int(data.get("spot", 0))
        action = data.get("action", "").lower()  # Expected: "buy_ce" or "buy_pe"
        quantity = int(data.get("quantity", 15))  # Default to 15

        if action not in ["buy_ce", "buy_pe"]:
            return jsonify({"error": "Invalid action"}), 400

        # Get option tokens
        ce_token, pe_token = get_tokens_from_spot(spot_price)
        token = ce_token if action == "buy_ce" else pe_token

        print(f"🎯 Action: {action} | Token: {token}")

        # === Build order payload ===
        order_payload = {
            "transactionType": "BUY",
            "orderType": "MARKET",
            "productType": "INTRADAY",
            "price": 0,
            "quantity": quantity,
            "triggerPrice": 0,
            "instrumentToken": token,
            "orderValidity": "DAY",
            "disclosedQuantity": 0,
            "afterMarketOrder": False,
            "amoTime": "OPEN",
            "trailingStopLoss": 0,
            "stopLoss": 0,
            "takeProfit": 0
        }

        # === Set request headers ===
        headers = {
            "Content-Type": "application/json",
            "access-token": DHAN_ACCESS_TOKEN,
            "client-id": DHAN_CLIENT_ID
        }

        # === Send order to Dhan API ===
        response = requests.post(PLACE_ORDER_URL, headers=headers, json=order_payload)
        print("✅ Order Response:", response.status_code, response.text)

        if response.status_code == 200:
            return jsonify({"message": "Order placed successfully"}), 200
        else:
            return jsonify({"error": response.text}), 500

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=False)
