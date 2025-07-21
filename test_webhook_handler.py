import pandas as pd

CSV_FILE = "api-scrip-master.csv"

def round_to_nearest_100(n):
    return int(round(n / 100.0)) * 100

def get_tokens_from_spot(spot_price):
    df = pd.read_csv(CSV_FILE)

    atm_strike = round_to_nearest_100(spot_price)
    expiry_str = "Jul2025"
    underlying_id = 26009

    def find_token(option_type):
        symbol_pattern = f"BANKNIFTY-{expiry_str}-{atm_strike}-{option_type}"
        row = df[
            (df["UNDERLYING_SECURITY_ID"] == underlying_id) &
            (df["SYMBOL_NAME"] == symbol_pattern)
        ]
        if not row.empty:
            return row.iloc[0]["DISPLAY_NAME"]
        return None

    ce_token = find_token("CE")
    pe_token = find_token("PE")

    return ce_token, pe_token
