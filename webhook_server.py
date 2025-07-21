from flask import Flask, request, jsonify
import requests
from test_webhook_handler import get_tokens_from_spot  # fetch CE/PE tokens from CSV

app = Flask(__name__)

# Replace with your actual Dhan API credentials
DHAN_CLIENT_ID = "YourClientID"
DHAN_ACCESS_TOKEN = "YourAccessToken"

# === Dhan API URLs ===
PLACE_ORDER_URL = "https://api.dhan.co/orders"

@app.route('/', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("📥 Incoming Webhook Data:", data)

        # Extract spot price from TradingView alert
        spot_price = int(data.get("spot", 0))
        action = data.get("action", "").lower()  # "buy_ce" or "buy_pe"
        quantity = int(data.get("quantity", 15))  # default to 15

        if action not in ["buy_ce", "buy_pe"]:
            return jsonify({"error": "Invalid action"}), 400

        # Get CE/PE tokens
        ce_token, pe_token = get_tokens_from_spot(spot_price)
        token = ce_token if action == "buy_ce" else pe_token

        print(f"🎯 Action: {action} | Token: {token}")

        # Construct order payload
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

        # Add headers
        headers = {
            "Content-Type": "application/json",
            "access-token": DHAN_ACCESS_TOKEN,
            "client-id": DHAN_CLIENT_ID
        }

        # Place order
        response = requests.post(PLACE_ORDER_URL, headers=headers, json=order_payload)
        print("✅ Order Placed | Response:", response.status_code, response.text)

        if response.status_code == 200:
            return jsonify({"message": "Order placed successfully"}), 200
        else:
            return jsonify({"error": response.text}), 500

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)
