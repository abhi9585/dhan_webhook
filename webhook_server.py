def get_banknifty_spot():
    try:
        url = f"{DHAN_BASE}/market-feed/quote/NSE_INDEX/Nifty Bank"
        headers = {"access-token": DHAN_TOKEN}
        print(f"Requesting URL: {url}")
        print(f"Using token: {DHAN_TOKEN[:6]}...")  # Don't print full token

        res = requests.get(url, headers=headers)
        print("Raw response:", res.text)  # <-- Add this

        data = res.json()
        ltp = float(data.get("dhan", {}).get("ltp", 0))
        return round(ltp / 100) * 100
    except Exception as e:
        print("Error fetching spot price:", e)
        return 0
