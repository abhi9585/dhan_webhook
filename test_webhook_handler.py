import pandas as pd
from datetime import datetime

# === Load CSV master ===
CSV_PATH = "api-scrip-master.csv"  # ensure this is deployed on Render
csv_df = pd.read_csv(CSV_PATH)

# === Set monthly expiry date (example: July 31, 2025) ===
raw_expiry = "2025-07-31"  # keep this updated manually or pass via TradingView later
EXPIRY_DATE = datetime.strptime(raw_expiry, "%Y-%m-%d").strftime("%#m/%#d/%Y")  # Windows-compatible

def get_tokens_from_spot(spot_price):
    # === Derive CE/PE strikes ===
    ce_strike = int(spot_price // 100) * 100
    pe_strike = ce_strike + 100  # you can also do -100 if needed

    print(f"📌 Spot: {spot_price}")
    print(f"💡 CE Strike: {ce_strike}, PE Strike: {pe_strike}")
    print(f"📆 Expiry: {EXPIRY_DATE}")

    # === Filter CE Row ===
    ce_row = csv_df[
        (csv_df["SYMBOL_NAME"].str.contains("BANKNIFTY", case=False)) &
        (csv_df["OPTION_TYPE"] == "CE") &
        (csv_df["STRIKE_PRICE"] == ce_strike) &
        (csv_df["SM_EXPIRY_DATE"] == EXPIRY_DATE)
    ]

    # === Filter PE Row ===
    pe_row = csv_df[
        (csv_df["SYMBOL_NAME"].str.contains("BANKNIFTY", case=False)) &
        (csv_df["OPTION_TYPE"] == "PE") &
        (csv_df["STRIKE_PRICE"] == pe_strike) &
        (csv_df["SM_EXPIRY_DATE"] == EXPIRY_DATE)
    ]

    # === Extract instrument tokens ===
    ce_token = int(ce_row["TOKEN"].values[0]) if not ce_row.empty else None
    pe_token = int(pe_row["TOKEN"].values[0]) if not pe_row.empty else None

    return ce_token, pe_token
