import pandas as pd

# Load CSV once during import
CSV_FILE = "api-scrip-master.csv"
EXPIRY_DATE = "7/31/2025"  # <- Modify only here for monthly expiry
df = pd.read_csv(CSV_FILE, low_memory=False)

def get_tokens_from_spot(spot_price: int, expiry: str = EXPIRY_DATE):
    """
    Given spot price, return CE and PE SECURITY_IDs for BankNifty ATM options (monthly expiry only)
    """
    # Round down to nearest 100
    atm_strike = int(spot_price / 100) * 100
    ce_strike = atm_strike
    pe_strike = ce_strike + 100

    # Filter CE
    ce_row = df[
        (df["SYMBOL_NAME"].str.contains("BANKNIFTY", case=False, na=False)) &
        (df["OPTION_TYPE"] == "CE") &
        (df["STRIKE_PRICE"] == ce_strike) &
        (df["SM_EXPIRY_DATE"] == expiry)
    ]

    # Filter PE
    pe_row = df[
        (df["SYMBOL_NAME"].str.contains("BANKNIFTY", case=False, na=False)) &
        (df["OPTION_TYPE"] == "PE") &
        (df["STRIKE_PRICE"] == pe_strike) &
        (df["SM_EXPIRY_DATE"] == expiry)
    ]

    if ce_row.empty or pe_row.empty:
        raise ValueError("CE or PE token not found for given spot price.")

    ce_token = ce_row.iloc[0]["SECURITY_ID"]
    pe_token = pe_row.iloc[0]["SECURITY_ID"]
    return ce_token, pe_token
