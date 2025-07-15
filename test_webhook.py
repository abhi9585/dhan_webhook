import requests

url = "https://dhan-webhook-final.onrender.com/webhook"

payload = {
    "direction": "BUY",
    "option_type": "CE",
    "expiry": "250717"
}

# 🔐 Add token to headers
headers = {
    "X-Webhook-Token": "my_9585_secure_token"
}

response = requests.post(url, json=payload, headers=headers)
print("Status Code:", response.status_code)
print("Response:", response.json())