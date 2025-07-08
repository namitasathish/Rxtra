import streamlit as st
from ocr.extractor import extract_text
from parser.prescription_parser import parse_prescription
from lookup.inventory import check_inventory
from lookup.alternatives import get_alternatives
from reminder.scheduler import schedule_reminder
from reminder.notifier import send_email
from utils.cart import Cart
from utils.formatter import format_prescription_info
import json
import pandas as pd
import datetime
import re

# --- Page & Layout Setup ---
st.set_page_config(page_title="Pharmacy Assistant", layout="wide")
# --- App Title & Subheadline ---
st.markdown("""
<h1 style='text-align: center;'>Rxtra</h1>
<h4 style='text-align: center; color: grey;'>The Extra Care Your Prescriptions Deserve<br><span style='color: #4CAF50;'>POWERED BY AI</span></h4>
""", unsafe_allow_html=True)


# --- Load Data ---
with open("data/side_effects.json") as f:
    side_effects_db = json.load(f)

# --- Session State Initialization ---
if "cart" not in st.session_state:
    st.session_state.cart = Cart()
if "info_list" not in st.session_state:
    st.session_state.info_list = []
if "cart_added" not in st.session_state:
    st.session_state.cart_added = []

# --- Sidebar: Input & Cart Summary ---
st.sidebar.header("📝 Add Medicine")

mode = st.sidebar.radio("Input method", ["Image Upload", "Manual"])
if mode == "Image Upload":
    img = st.sidebar.file_uploader("Prescription Image", type=["png","jpg","jpeg"])
    if img:
        text = extract_text(img)
        st.sidebar.markdown(f"**Extracted:** {text}")
        info = parse_prescription(text)
        if st.sidebar.button("➕ Add from Image"):
            st.session_state.info_list.append(info)
else:
    med = st.sidebar.text_input("Medicine Name")
    dose = st.sidebar.number_input("Dosage (mg)", min_value=1, step=1)
    freq = st.sidebar.number_input("Frequency/day", min_value=1, step=1)
    dur = st.sidebar.number_input("Duration (days)", min_value=1, step=1)
    if st.sidebar.button("➕ Add Manually"):
        st.session_state.info_list.append({
            "medicine": med,
            "dosage_mg": dose,
            "frequency_per_day": freq,
            "duration_days": dur,
            "quantity": freq * dur
        })

# Sticky Cart Summary
if st.session_state.cart.items:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛒 Cart Summary")
    for item in st.session_state.cart.items:
        st.sidebar.markdown(f"- {item['medicine']} x{item['quantity']} = ₹{item['total_price']}")
    total = sum(i['total_price'] for i in st.session_state.cart.items if isinstance(i['total_price'], (int, float)))
    st.sidebar.markdown(f"**Total: ₹{total:.2f}**")

# --- Main: Progress Indicator ---
num = len(st.session_state.info_list)
max_med = 5
st.markdown(f"**Medicines added: {num}**")

# --- Main: Tabs ---
tabs = st.tabs(["💊 Medicines", "🛒 Cart", "⏰ Reminders"])

# --- Tab 1: Medicines ---
with tabs[0]:
    st.header("1️⃣ Your Medicines")
    if not st.session_state.info_list:
        st.info("Use the sidebar to add medicines.")
    for i, info in enumerate(st.session_state.info_list):
        with st.container():
            c1, c2 = st.columns([3,1])
            with c1:
                st.subheader(f"{info['medicine']} — {info['dosage_mg']}mg")
                st.markdown(
                    f"- **Qty:** {info['quantity']}  "
                    f"- **Freq:** {info['frequency_per_day']}/day  "
                    f"- **Dur:** {info['duration_days']} days"
                )
            with c2:
                if st.button("❌ Remove", key=f"rm_med_{i}"):
                    st.session_state.info_list.pop(i)
                    if i in st.session_state.cart_added:
                        st.session_state.cart.remove(i)
                        st.session_state.cart_added.remove(i)
                    

        # Availability & Alternatives
        with st.expander("Check Stock & Alternatives", expanded=False):
            avail, price, stock = check_inventory(info)
            if avail and stock >= info["quantity"]:
                st.success(f"In stock: {stock} @ ₹{price}/unit")
                if i in st.session_state.cart_added:
                    st.info("✅ Already in cart")
                else:
                    if st.button("➕ Add to Cart", key=f"add_cart_{i}"):
                        st.session_state.cart.add(info["medicine"], info["quantity"], price)
                        st.session_state.cart_added.append(i)
                        st.success(f"✅ Added {info['medicine']} to cart")
            else:
                st.warning(f"Only {stock} available" if avail else "Out of stock")
                if stock > 0:
                    if st.button("Add Available Qty", key=f"add_avail_{i}"):
                        st.session_state.cart.add(info["medicine"], stock, price)
                        st.session_state.cart_added.append(i)
                        st.success(f"✅ Added {stock} of {info['medicine']} to cart")
                alts = get_alternatives(info["medicine"])
                if alts:
                    choice = st.selectbox("Or choose alternative", alts, key=f"alt_med_{i}")
                    if st.button("➕ Add Alternative", key=f"add_alt_{i}"):
                        st.session_state.cart.add(choice, 1, None)
                        st.session_state.cart_added.append(i)
                        st.success(f"✅ Added alternative {choice}")

        # Cart Confirmation
        if i in st.session_state.cart_added:
            st.markdown(f"🛒 **{info['medicine']}** is in your cart")

        # Side Effects
        with st.expander("View Side Effects", expanded=False):
            data = side_effects_db.get(info["medicine"], {})
            common = data.get("common_side_effects", [])
            serious = data.get("serious_side_effects", [])
            warn = data.get("warnings", "")

            st.markdown("**🟢 Common:**")
            st.markdown("\n".join([f"- {e}" for e in common]) or "_None_")

            st.markdown("**🔴 Serious:**")
            st.markdown("\n".join([f"- {e}" for e in serious]) or "_None_")

            if warn:
                st.markdown("**⚠️ Warnings:**")
                st.warning(warn)

# --- Tab 2: Cart ---
with tabs[1]:
    st.header("2️⃣ Cart")
    items = st.session_state.cart.items
    if not items:
        st.info("Your cart is empty.")
    else:
        df = pd.DataFrame(items).rename(columns={
            "medicine":"Medicine","quantity":"Qty",
            "price_per_unit":"Price/unit","total_price":"Total"
        })
        st.table(df)
        total = df["Total"].sum()
        st.metric("🧾 Cart Total", f"₹{total:.2f}")

# --- Tab 3: Reminders ---
with tabs[2]:
    st.header("3️⃣ Set Reminders")
    if not st.session_state.cart.items:
        st.info("Add items to your cart first.")
    else:
        # Email Input
        email = st.text_input("📧 Your email for reminders", key="user_email")
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.error("❌ Please enter a valid email address.")

        for i, info in enumerate(st.session_state.info_list):
            with st.expander(f"Set for {info['medicine']}", expanded=False):
                sd = st.date_input("📅 Start Date", key=f"sd_{i}")
                time_str = st.text_input("⏰ Time (HH:MM)", "09:00", key=f"tm_{i}")
                if re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", time_str):
                    tm = datetime.datetime.strptime(time_str, "%H:%M").time()
                    if email and st.button("Set Reminder", key=f"set_{i}"):
                        info_copy = info.copy(); info_copy["email"] = email
                        schedule_reminder(info_copy, sd, tm, send_email)
                        st.success(f"⏰ Reminder set for {info['medicine']} at {sd} {tm.strftime('%H:%M')}")
                else:
                    st.error("⚠️ Invalid time format (use HH:MM)")

