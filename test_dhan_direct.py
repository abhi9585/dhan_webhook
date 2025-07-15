import requests

DHAN_TOKEN = "your_actual_access_token_here"  # ← paste your token

url = "https://api.dhan.co/market-feed/quotes"
headers = {
    "access-token": DHAN_TOKEN,
    "Content-Type": "application/json"
}
payload = {
    "security_id": "NSE_INDEX|26009"
}

print("➡ Sending request to:", url)
print("📨 Headers:", headers)
print("📦 Payload:", payload)

response = requests.post(url, headers=headers, json=payload)

print("🌐 Status Code:", response.status_code)
print("📄 Raw Text:", response.text)

try:
    print("🧾 Parsed JSON:", response.json())
except Exception as e:
    print("❌ Failed to parse JSON:", e)
