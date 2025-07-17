import requests

# Your deployed webhook URL
url = "https://dhan-webhook-final-oop9.onrender.com/webhook"

# Example payload to test buy CE order
payload = {
    "direction": "BUY",        # or "SELL"
    "option_type": "CE",       # or "PE"
    "expiry": "250718"         # format: YYMMDD
}

try:
    print("Sending POST request to:", url)
    response = requests.post(url, json=payload)

    print("Raw Response:", response.text)
    try:
        print("Parsed JSON:", response.json())
    except Exception as e:
        print("JSON parsing error:", e)

except Exception as e:
    print("Request failed:", e)
