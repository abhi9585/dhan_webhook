import pandas as pd

# Load CSV once globally for performance
CSV_FILE = "api-scrip-master.csv"
EXPIRY_DATE = "7/31/2025"  # Set monthly expiry here

# Load CSV
try:
    df = pd.read_csv(CSV_FILE, low_memory=False)
    print(f"✅ Loaded {CSV_FILE} with {len(df)} rows.")
except Exception as e:
    print(f"❌ Failed to load CSV: {e}")
    df = pd.DataFrame()


def get_tokens_from_spot(spot_price, csv_df=None):
    """
    Given a BankNifty spot price, return CE and PE instrument tokens.
    Returns (ce_token, pe_token) or (None, None) if not found.
    """

    if csv_df is None:
        csv_df = df

    if csv_df.empty:
        print("❌ CSV is empty or not loaded.")
        return None, None

    # === Derive CE/PE Strikes ===
    ce_strike = int(spot_price // 100) * 100
    pe_strike = ce_strike + 100

    print(f"\n🎯 Spot: {spot_price}")
    print(f"👉 CE Strike: {ce_strike}, PE Strike: {pe_strike}")
    print(f"📅 Expiry: {EXPIRY_DATE}")

    # === Filter rows ===
    ce_row = csv_df[
        (csv_df["SYMBOL_NAME"].str.contains("BANKNIFTY", case=False, na=False)) &
        (csv_df["OPTION_TYPE"] == "CE") &
        (csv_df["STRIKE_PRICE"] == ce_strike) &
        (csv_df["SM_EXPIRY_DATE"] == EXPIRY_DATE)
    ]

    pe_row = csv_df[
        (csv_df["SYMBOL_NAME"].str.contains("BANKNIFTY", case=False, na=False)) &
        (csv_df["OPTION_TYPE"] == "PE") &
        (csv_df["STRIKE_PRICE"] == pe_strike) &
        (csv_df["SM_EXPIRY_DATE"] == EXPIRY_DATE)
    ]

    ce_token = ce_row.iloc[0]["SECURITY_ID"] if not ce_row.empty else None
    pe_token = pe_row.iloc[0]["SECURITY_ID"] if not pe_row.empty else None

    if ce_token: print(f"✅ CE Token: {ce_token}")
    else: print("❌ CE token not found")

    if pe_token: print(f"✅ PE Token: {pe_token}")
    else: print("❌ PE token not found")

    return ce_token, pe_token


# === If testing standalone ===
if _name_ == "_main_":
    try:
        spot = int(input("📥 Enter BankNifty spot price: "))
        get_tokens_from_spot(spot)
    except Exception as e:
        print("❌ Error:", e)
