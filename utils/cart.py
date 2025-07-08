import pandas as pd
import streamlit as st

class Cart:
    def __init__(self):
        self.items = []

    def add(self, med, qty, price_per_unit):
        total = round(qty * price_per_unit, 2) if price_per_unit else "N/A"
        self.items.append({
            "medicine": med,
            "quantity": qty,
            "price_per_unit": price_per_unit,
            "total_price": total
        })

    def remove(self, index):
        if 0 <= index < len(self.items):
            del self.items[index]

    def suggest(self):
        df = pd.DataFrame(self.items)
        if not df.empty and "Vitamin D" not in df["medicine"].values:
            st.info("🔔 You often buy Vitamin D — add it to your order?")
