import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import datetime
import os
import random

# Set Tesseract path (Windows only)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Quotes and flags
quotes = [
    "Money speaks only one language: 'If you save me today, I'll save you tomorrow.'",
    "Sis, your wallet’s crying louder than your love life.",
    "Budgeting is the new black.",
    "Did you just drop $60 on scented candles? Girl, he ain’t coming back.",
    "Look at you, making financially responsible choices. Sugar daddies everywhere are trembling.",
    "‘Treat yourself’ doesn’t mean bankrupt yourself.",
    "If you can't afford it twice, you can't afford it once.",
    "Track your spending. If you can scroll TikTok for hours, you can do that too.",
    "Your bank account called. It's filing a restraining order.",
    "Every swipe is a red flag and girl, you're ignoring all of them.",
    "Money is energy — yours is clearly chaotic right now.",
    "Clarity is queen. Know where every dollar goes before it ghosts you.",
    "Financial freedom hits different when you're not dodging calls from the bank.",
    "Money doesn't grow on trees—but your regret sure do."
]

red_flags = ["casino", "gamble", "lotto", "bet", "crypto", "loan shark", "strip club", "vape", "onlyfans"]

# Session-based transaction storage
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# ---------- Functions ---------- #
def add_transaction(date, details, amount, category, gender):
    entry = {
        "Date": date,
        "Details": details,
        "Amount": f"${amount:.2f}",
        "Category": category,
        "Gender": gender
    }
    st.session_state.transactions.append(entry)

    roast = ""
    if "boba" in details.lower() or "bubble tea" in details.lower():
        if gender == "Female":
            roast = "💅 $ on boba again? Sis, he's not worth it."
        elif gender == "Male":
            roast = "Bro... another boba? She ain't texting back."
        else:
            roast = "Another boba? You living dangerously, darling."
    
    return f"Transaction logged. Spenderella approves (or judges).\n\n{roast}"

def extract_receipt_text(img):
    if img is None:
        return ""
    return pytesseract.image_to_string(img)

def process_ocr_text(text, category, gender):
    today = datetime.date.today()
    entry = {
        "Date": today,
        "Details": text,
        "Amount": "Unknown",
        "Category": category,
        "Gender": gender
    }
    st.session_state.transactions.append(entry)
    return f"Receipt logged. Spenderella's watching you 👀\n\nSaved text:\n{text}"

def show_transactions():
    if not st.session_state.transactions:
        return pd.DataFrame(columns=["Date", "Details", "Amount", "Category", "Gender"])
    return pd.DataFrame(st.session_state.transactions)

def weekly_breakdown():
    df = show_transactions()
    df["Date"] = pd.to_datetime(df["Date"])
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    recent = df[df["Date"] >= one_week_ago]
    return recent.groupby("Category").size().reset_index(name="Count")

def detect_red_flags():
    df = show_transactions()
    flagged = df[df["Details"].str.lower().apply(lambda x: any(flag in x for flag in red_flags))]
    return flagged

# ---------- Streamlit UI ---------- #
st.set_page_config(page_title="Spenderella", layout="centered")
st.title("\U0001F4B8 Spenderella: Your Sassy Financial Frenemy")
st.subheader(random.choice(quotes))

tabs = st.tabs(["📸 OCR Receipt Upload", "✍ Manual Entry", "📊 View Transactions", "📈 Weekly Breakdown", "🚩 Red Flags"])

# OCR Receipt Upload
tab = tabs[0]
with tab:
    st.header("OCR Receipt Upload")
    img = st.file_uploader("Upload your receipt image")
    if img:
        img = Image.open(img)
        text = extract_receipt_text(img)
        st.text_area("Detected / Editable Text", value=text, key="ocr_text")
        cat = st.selectbox("Category", ["Food", "Clothing", "Entertainment", "Bills", "Other"], key="ocr_cat")
        gender = st.radio("Your Gender", ["Female", "Male", "Other"], key="ocr_gen")
        if st.button("Save Transaction from OCR"):
            msg = process_ocr_text(st.session_state.ocr_text, cat, gender)
            st.success(msg)

# Manual Entry
tab = tabs[1]
with tab:
    st.header("Manual Transaction Entry")
    date = st.text_input("Date (YYYY-MM-DD)", value=str(datetime.date.today()))
    details = st.text_input("Item / Description")
    amount = st.number_input("Amount Spent", min_value=0.01)
    cat = st.selectbox("Category", ["Food", "Clothing", "Entertainment", "Bills", "Other"])
    gender = st.radio("Your Gender", ["Female", "Male", "Other"])
    if st.button("Add Transaction"):
        try:
            parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            msg = add_transaction(parsed_date, details, amount, cat, gender)
            st.success(msg)
        except:
            st.error("Invalid date format. Use YYYY-MM-DD.")

# View Transactions
tab = tabs[2]
with tab:
    st.header("Transaction Log")
    df = show_transactions()
    st.dataframe(df)

# Weekly Breakdown
tab = tabs[3]
with tab:
    st.header("Weekly Category Breakdown")
    breakdown = weekly_breakdown()
    st.dataframe(breakdown)

# Red Flag Detection
tab = tabs[4]
with tab:
    st.header("Financial Red Flags")
    red_df = detect_red_flags()
    st.dataframe(red_df)

st.caption("Made with 💅 by Spenderella 2025")
