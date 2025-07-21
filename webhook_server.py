# webhook_server.py
import os
from flask import Flask, request, jsonify
import requests

app = Flask(_name_)

# Load from environment
DHAN_CLIENT_ID = os.environ.get("DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN = os.environ.get("DHAN_ACCESS_TOKEN")

headers = {
    "accept": "application/json",
    "access-token": DHAN_ACCESS_TOKEN,
    "client-id": DHAN_CLIENT_ID,
    "Content-Type": "application/json"
}

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📩 Webhook received:", data)

    try:
        # Extract and sanitize data
        symbol = data.get('symbol')
        side = data.get('side')  # BUY or SELL
        exchange_segment = "NSE_OPTION"
        product_type = "INTRADAY"
        order_type = "MARKET"
        validity = "DAY"
        quantity = 30

        order_payload = {
            "securityId": symbol,
            "exchangeSegment": exchange_segment,
            "orderType": order_type,
            "productType": product_type,
            "transactionType": side.upper(),
            "validity": validity,
            "quantity": quantity,
            "price": 0,
            "triggerPrice": 0,
            "afterMarketOrder": False,
            "amoTime": "OPEN"
        }

        print("📤 Sending order:", order_payload)
        response = requests.post(
            "https://api.dhan.co/orders",
            headers=headers,
            json=order_payload
        )

        print("📥 Order response:", response.text)
        return jsonify(response.json()), response.status_code

    except Exception as e:
        print("❌ Error placing order:", e)
        return jsonify({"error": str(e)}), 500

if _name_ == '_main_':
    app.run(port=10000, debug=True)
