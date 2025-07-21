from flask import Flask, request, jsonify
import requests
import os
from test_webhook_handler import get_tokens_from_spot  # Function to fetch CE/PE tokens from CSV

app = Flask(__name__)

# === Load credentials from environment variables ===
DHAN_CLIENT_ID = os.environ.get("DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN = os.environ.get("DHAN_ACCESS_TOKEN")

# === Dhan API endpoint ===
PLACE_ORDER_URL = "https://api.dhan.co/orders"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("📥 Incoming Webhook Data:", data)

        # === Extract data from the webhook payload ===
        spot_price = int(data.get("spot", 0))
        action = data.get("action", "").lower()  # "buy_ce" or "buy_pe"
        quantity = int(data.get("quantity", 15))  # default to 15

        if action not in ["buy_ce", "buy_pe"]:
            return jsonify({"error": "Invalid action"}), 400

        # === Get instrument token from CSV lookup ===
        ce_token, pe_token = get_tokens_from_spot(spot_price)
        token = ce_token if action == "buy_ce" else pe_token

        print(f"🎯 Action: {action} | Spot: {spot_price} | Token Used: {token}")

        # === Construct order payload ===
order_payload = {
    "transactionType": "BUY",
    "exchangeSegment": "NSE_OPT",  # ✅ ADD THIS LINE
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

        # === Log headers for debug (Optional) ===
        print("🧪 Headers Sent:", headers)
        print("📦 Order Payload:", order_payload)

        # === Place order ===
        response = requests.post(PLACE_ORDER_URL, headers=headers, json=order_payload)
        print("✅ Dhan API Response:", response.status_code, response.text)

        if response.status_code == 200:
            return jsonify({"message": "Order placed successfully"}), 200
        else:
            return jsonify({"error": response.text}), 500

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=False)
