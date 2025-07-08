import pandas as pd

df = pd.read_csv("data/medicine_database.csv")

def check_inventory(info: dict):
    med = info["medicine"]
    dosage = info["dosage_mg"]
    quantity = info["quantity"]

    # Use correct column names from your CSV
    rec = df[(df["medicine_name"] == med) & (df["strength_mg"] == dosage)]

    if rec.empty:
        return False, None, 0

    stock = int(rec["stock_level"].values[0])
    price = float(rec["price_inr"].values[0])
    return True, price, stock
