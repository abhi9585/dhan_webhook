from flask import Flask, request, jsonify
import requests
import os
import math

app = Flask(__name__)

# Get secrets from environment
API_KEY = os.getenv("DHAN_API_KEY")
CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCOUNT_ID = os.getenv("DHAN_ACCOUNT_ID")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    try:
        spot = float(data.get("spot_price"))

        ce_strike = math.floor(spot / 100) * 100
        pe_strike = math.ceil(spot / 100) * 100

        if 53300 <= spot < 53400:
            ce_strike = 53300
            pe_strike = 54000

        # Prepare Dhan Order
        url = "https://api.dhan.co/orders"
        headers = {
            "accept": "application/json",
            "access-token": API_KEY,
            "Content-Type": "application/json"
        }

        # Sample order body (CE example)
        ce_order = {
            "accountId": ACCOUNT_ID,
            "symbol": f"BANKNIFTY25JUL{ce_strike}CE",
            "transactionType": "BUY",
            "orderType": "MARKET",
            "quantity": 30,
            "exchangeSegment": "NFO",
            "productType": "INTRADAY"
        }

        response = requests.post(url, headers=headers, json=ce_order)
        return jsonify({
            "spot": spot,
            "ce": ce_strike,
            "pe": pe_strike,
            "dhan_response": response.json()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
