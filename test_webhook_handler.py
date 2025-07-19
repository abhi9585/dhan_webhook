import pandas as pd

# === STEP 1: Load the CSV file ===
csv_file = "api-scrip-master.csv"
df = pd.read_csv(csv_file, low_memory=False)

print(f"\n📋 Loaded CSV Columns: {list(df.columns)}")

# === STEP 2: Ask for Spot Price from User ===
spot = int(input("\n📥 Enter current BankNifty Spot: "))

# === STEP 3: Set Monthly Expiry (Must match CSV exactly) ===
expiry = "7/31/2025"

# === STEP 4: Derive ATM ITM Strikes based on custom logic ===
# CE: Spot 53300–53399 → CE = 53300 (ITM logic → one step below)
# PE: PE = CE + 100 (which means OTM for PE = ITM)
atm_strike = int(spot / 100) * 100

# You can tweak this logic as per strategy
ce_strike = atm_strike if (spot % 100) < 100 else atm_strike
pe_strike = ce_strike + 100  # ITM PE: far OTM, you can reverse if needed

print(f"\n🎯 Spot from alert: {spot}")
print(f"👉 ITM CE Strike: {ce_strike}")
print(f"👉 ITM PE Strike: {pe_strike}")

# === STEP 5: Find CE and PE Rows ===
ce_row = df[
    (df["SYMBOL_NAME"].str.contains("BANKNIFTY", case=False, na=False)) &
    (df["OPTION_TYPE"] == "CE") &
    (df["STRIKE_PRICE"] == ce_strike) &
    (df["SM_EXPIRY_DATE"] == expiry)
]

pe_row = df[
    (df["SYMBOL_NAME"].str.contains("BANKNIFTY", case=False, na=False)) &
    (df["OPTION_TYPE"] == "PE") &
    (df["STRIKE_PRICE"] == pe_strike) &
    (df["SM_EXPIRY_DATE"] == expiry)
]

# === STEP 6: Output Tokens ===
print("\n✅ ITM CE/PE Token Results:\n")

if not ce_row.empty:
    print(f"✅ CE: {ce_row.iloc[0]['SYMBOL_NAME']} | Token: {ce_row.iloc[0]['SECURITY_ID']}")
else:
    print("❌ ITM CE not found")

if not pe_row.empty:
    print(f"✅ PE: {pe_row.iloc[0]['SYMBOL_NAME']} | Token: {pe_row.iloc[0]['SECURITY_ID']}")
else:
    print("❌ ITM PE not found")