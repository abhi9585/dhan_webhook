def get_banknifty_spot():
    try:
        import requests, os

        url = "https://api.dhan.co/market-feed/quote/NSE_INDEX/NIFTY_BANK"
        headers = {
            "access-token": os.getenv("DHAN_TOKEN")
        }

        response = requests.get(url, headers=headers)
        print("Raw Response:", response.text)
        print("Status Code:", response.status_code)

        if response.status_code != 200:
            return 0

        data = response.json()
        ltp = float(data.get("dhan", {}).get("ltp", 0))
        return round(ltp / 100) * 100
    except Exception as e:
        print("Error in get_banknifty_spot:", e)
        return 0