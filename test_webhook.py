def get_banknifty_spot():
    try:
        url = f"{DHAN_BASE}/market-feed/quote/NSE_INDEX/Nifty Bank"
        headers = {"access-token": DHAN_TOKEN}
        
        res = requests.get(url, headers=headers)
        print("🔍 Raw Spot Response:", res.status_code, res.text)  # 🔴 LOG ADDED
        
        data = res.json()
        ltp = float(data.get("dhan", {}).get("ltp", 0))
        return round(ltp / 100) * 100
    except Exception as e:
        print("❌ Error fetching spot price:", e)
        return 0