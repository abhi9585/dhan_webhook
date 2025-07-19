from flask import Flask, request, jsonify
import csv
import os
import requests
from datetime import datetime

app = Flask(__name__)

# Load credentials from environment
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

CSV_FILE = 'api-scrip-master.csv'
EXPIRY_DATE = '2025-07-25'  # monthly expiry

def get_instrument_token(strike_price, option_type):
    with open(CSV_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if (
                row['TRADING_SYMBOL'].startswith('BANKNIFTY') and
                row['SM_EXPIRY_DATE'] == EXPIRY_DATE and
                row['OPTION_TYPE'] == option_type and
                int(row['STRIKE_PRICE']) == strike_price
            ):
                return row['INSTRUMENT_TOKEN']
    return None

def place_order(token, option_type):
    url = "https://api.dhan.co/orders"

    payload = {
        "transactionType": "BUY",
        "exchangeSegment": "NFO",
        "productType": "INTRADAY",
        "orderType": "MARKET",
        "validity": "DAY",
        "securityId": token,
        "quantity": 30,
        "price": 0,
        "afterMarketOrder": False,
        "disclosedQuantity": 0,
        "triggerPrice": 0,
        "boProfitValue": 0,
        "boStopLossValue": 0,
        "orderSource": "API"
    }

    headers = {
        "access-token": DHAN_ACCESS_TOKEN,
        "Content-Type": "application/json",
        "client-id": DHAN_CLIENT_ID
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        spot = float(data.get("spot", 0))
        side = data.get("side", "").upper()

        atm_strike = round(spot / 100) * 100
        option_type = "CE" if side == "BUY" else "PE"

        token = get_instrument_token(atm_strike, option_type)
        if not token:
            return jsonify({"error": "Instrument token not found"}), 404

        result = place_order(token, option_type)
        return jsonify({"status": "Order Placed", "details": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return '🚀 Webhook Server is Running'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
