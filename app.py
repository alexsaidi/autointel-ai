import os
import sys
import logging
import random
import requests
import streamlit as st
from openai import OpenAI
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

# ------------------------------------------------------------
# 1. CONFIG & CONSTANTS
# ------------------------------------------------------------
st.set_page_config(page_title="AutoIntel.AI Car Dashboard", layout="wide")

# Magic numbers and strings pulled into constants
MIN_YEAR = 2012
MAX_YEAR = 2024
MIN_PRICE = 15000
MAX_PRICE = 45000
LISTINGS_DEFAULT_COUNT = 5

MAKES_MODELS = {
    "Toyota": ["Camry", "Corolla"],
    "Honda": ["Civic", "Accord"],
    "Ford": ["Mustang", "F-150"],
    "BMW": ["3 Series", "X5"],
}
LOCATIONS = ["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX"]

OPENAI_API_KEY = (
    st.secrets.get("openai", {}).get("api_key")
    or os.getenv("OPENAI_API_KEY", "")
)
VIN_API_BASE = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/"

# ------------------------------------------------------------
# 2. EARLY ERROR HANDLING
# ------------------------------------------------------------
if not OPENAI_API_KEY:
    st.error("❌ OpenAI API key missing. Please set `OPENAI_API_KEY` in Streamlit secrets or environment.")
    st.stop()

# ------------------------------------------------------------
# 3. LOGGING
# ------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("AutoIntelAI")

# ------------------------------------------------------------
# 4. DATA MODELS
# ------------------------------------------------------------
class CarListing(BaseModel):
    id: int
    make: str
    model: str
    year: int
    price: float
    mileage: int
    location: str
    vin: Optional[str]
    image_url: Optional[str]
    features: List[str] = Field(default_factory=list)

class VINDecodeResult(BaseModel):
    VIN: str
    Make: Optional[str]
    Model: Optional[str]
    ModelYear: Optional[str]
    BodyClass: Optional[str]
    Error: Optional[str]

# ------------------------------------------------------------
# 5. DATA UTILITIES
# ------------------------------------------------------------
@st.cache_data(ttl=600)
def generate_random_car(i: int) -> CarListing:
    make = random.choice(list(MAKES_MODELS.keys()))
    model = random.choice(MAKES_MODELS[make])
    year = random.randint(MIN_YEAR, MAX_YEAR)
    price = round(random.uniform(MIN_PRICE, MAX_PRICE), 2)
    mileage = random.randint(5000, 120000)
    location = random.choice(LOCATIONS)
    vin = f"{random.randint(10**16, 10**17 - 1):017d}"
    image_url = f"https://source.unsplash.com/featured/?{make},{model},car"
    return CarListing(
        id=i, make=make, model=model, year=year,
        price=price, mileage=mileage, location=location,
        vin=vin, image_url=image_url
    )

def generate_listings(n: int = LISTINGS_DEFAULT_COUNT) -> List[CarListing]:
    return [generate_random_car(i) for i in range(1, n + 1)]

@st.cache_data(ttl=3600)
def decode_vin(vin: str) -> VINDecodeResult:
    resp = requests.get(f"{VIN_API_BASE}{vin}?format=json", timeout=10)
    resp.raise_for_status()
    data = resp.json().get("Results", [{}])[0]
    return VINDecodeResult(
        VIN=vin,
        Make=data.get("Make"),
        Model=data.get("Model"),
        ModelYear=data.get("ModelYear"),
        BodyClass=data.get("BodyClass"),
        Error=None,
    )

# ------------------------------------------------------------
# 6. AI UTILITIES (GPT-4)
# ------------------------------------------------------------
@st.cache_resource
def get_openai_client() -> OpenAI:
    return OpenAI(api_key=OPENAI_API_KEY)

def simple_keyword_response(text: str) -> Optional[str]:
    t = text.lower()
    if "price" in t:
        return "Prices fluctuate—see the Listings tab for up-to-date figures."
    if "mileage" in t:
        return "Mileage impacts value—lower mileage often means higher price."
    if any(g in t for g in ("hello", "hi")):
        return "Hello! How can I assist you with car listings today?"
    return None

def ask_openai(history: List[Dict[str, str]]) -> str:
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=history,
        max_tokens=250,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def get_ai_response(user_msg: str, history: List[Dict[str, str]]) -> str:
    if kr := simple_keyword_response(user_msg):
        history.append({"role": "assistant", "content": kr})
        return kr
    history.append({"role": "user", "content": user_msg})
    reply = ask_openai(history)
    history.append({"role": "assistant", "content": reply})
    return reply

# ------------------------------------------------------------
# 7. UI HELPERS
# ------------------------------------------------------------
def display_metrics(listings: List[CarListing]):
    if not listings:
        st.warning("No listings to display metrics.")
        return
    avg = sum(l.price for l in listings) / len(listings)
    hi = max(listings, key=lambda l: l.price)
    lo = min(listings, key=lambda l: l.price)
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Price", f"${avg:,.0f}")
    c2.metric("Highest Price", f"${hi.price:,.0f}", f"{hi.year} {hi.make}")
    c3.metric("Lowest Price", f"${lo.price:,.0f}", f"{lo.year} {lo.make}")

def display_listing(listing: CarListing):
    cols = st.columns([2, 4, 1, 1, 2])
    if listing.image_url:
        cols[0].image(listing.image_url, use_column_width=True)
    cols[1].markdown(f"**{listing.year} {listing.make} {listing.model}**")
    cols[2].write(f"${listing.price:,.0f}")
    cols[3].write(f"{listing.mileage:,} mi")
    cols[4].write(listing.location)

# ------------------------------------------------------------
# 8. MAIN APP LAYOUT & LOGIC
# ------------------------------------------------------------

st.title("🕵️ AutoIntel.AI Car Intelligence Dashboard")
tabs = st.tabs([
    "Track Listings",
    "AI Assistant",
    "VIN Decoder",
    "Deal Alerts",
    "Self-Enhancement",
    "Live OCR Sourcing"
])

# --- Track Listings Tab ---
with tabs[0]:
    st.header("Track Listings")
    if "prev_listings" not in st.session_state:
        st.session_state.prev_listings = []
    if "current_listings" not in st.session_state:
        st.session_state.current_listings = generate_listings(LISTINGS_DEFAULT_COUNT)

    if st.button("🔄 Refresh Listings"):
        st.session_state.prev_listings = st.session_state.current_listings
        count = len(st.session_state.current_listings)
        st.session_state.current_listings = generate_listings(count)

    prev_ids = {c.id for c in st.session_state.prev_listings}
    curr_ids = {c.id for c in st.session_state.current_listings}
    new = [c for c in st.session_state.current_listings if c.id not in prev_ids]
    sold = [c for c in st.session_state.prev_listings if c.id not in curr_ids]

    display_metrics(st.session_state.current_listings)
    st.subheader("Current Listings")
    for lst in st.session_state.current_listings:
        display_listing(lst)

    if new:
        st.subheader("🆕 New Since Last")
        for lst in new:
            display_listing(lst)
    if sold:
        st.subheader("✅ Removed/Sold")
        for lst in sold:
            display_listing(lst)

# --- AI Assistant Tab ---
with tabs[1]:
    st.header("AI Assistant")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "You are an expert car listings assistant."}
        ]
    query = st.text_input("Enter your question:")
    if st.button("Ask AI") and query:
        answer = get_ai_response(query, st.session_state.chat_history)

    for msg in st.session_state.chat_history:
        tag = "**You:**" if msg["role"] == "user" else "**AI:**"
        st.markdown(f"{tag} {msg['content']}")

# --- VIN Decoder Tab ---
with tabs[2]:
    st.header("VIN Decoder")
    vin_input = st.text_input("Enter a 17-character VIN:")
    if st.button("Decode VIN") and vin_input.strip():
        try:
            vin_data = decode_vin(vin_input.strip())
            st.subheader("Decoded VIN Information")
            for field, val in vin_data.dict().items():
                if val is not None:
                    st.write(f"**{field}:** {val}")
        except requests.HTTPError as err:
            st.error(f"API error: {err}")

# --- Deal Alerts Tab ---
with tabs[3]:
    st.header("Deal Alerts")
    sample_listings = generate_listings(8)
    options = [
        f"{l.year} {l.make} {l.model} — ${l.price:,.0f}"
        for l in sample_listings
    ]
    choice = st.selectbox("Choose a listing:", options)
    threshold = st.number_input("Your max price ($):", min_value=0.0, step=500.0)
    if st.button("Check Deal"):
        idx = options.index(choice)
        pick = sample_listings[idx]
        if pick.price <= threshold:
            st.success(f"🎉 Deal! {pick.year} {pick.make} at ${pick.price:,.0f}")
        else:
            st.info(f"❌ No deal: it's ${pick.price:,.0f}")

# --- Self-Enhancement Tab ---
with tabs[4]:
    st.header("AI-Powered Code Review")
    uploaded = st.file_uploader("Upload a Python file", type=["py"])
    if uploaded:
        code = uploaded.read().decode("utf-8")
    else:
        code = st.text_area("Or paste your Python code here", height=200)

    if st.button("Analyze Code"):
        if not code.strip():
            st.warning("Please upload or paste your code first.")
        else:
            try:
                client = get_openai_client()
                prompt = (
                    "You are an expert Python code reviewer. Analyze the following code and provide:\n"
                    "1. Maintainability score (1-10) and Performance score (1-10).\n"
                    "2. A bullet-point list of code quality suggestions.\n"
                    "3. Specific comments on caching, modularization, type hints, error handling, logging, and testing readiness.\n"
                    "4. (Optional) Improved code snippets or diff-style recommendations.\n\n"
                    f"```python\n{code}\n```"
                )
                with st.spinner("Reviewing code with GPT-4..."):
                    resp = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant for code review."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.5,
                    )
                    review = resp.choices[0].message.content.strip()

                lines = review.splitlines()
                review_body = review
                if lines and "Maintainability" in lines[0] and "Performance" in lines[0]:
                    try:
                        parts = lines[0].split(",")
                        m_scr = parts[0].split(":")[1].strip()
                        p_scr = parts[1].split(":")[1].strip()
                        st.subheader("Review Scores")
                        c1, c2 = st.columns(2)
                        c1.metric("Maintainability", m_scr)
                        c2.metric("Performance", p_scr)
                        review_body = "\n".join(lines[1:]).strip()
                    except Exception:
                        review_body = review

                st.subheader("Suggestions & Details")
                st.markdown(review_body)

                if "```diff" in review_body:
                    diff = review_body.split("```diff", 1)[1].rsplit("```", 1)[0]
                    st.subheader("Code Diff Suggestions")
                    st.code(diff, language="diff")
                elif "```python" in review_body:
                    snippets = review_body.split("```python")[1:]
                    for i, snip in enumerate(snippets):
                        snippet = snip.rsplit("```", 1)[0]
                        st.subheader(f"Code Snippet {i+1}")
                        st.code(snippet, language="python")

            except Exception as e:
                st.error(f"Error during code review: {e}")

# --- Live OCR Sourcing Tab ---
with tabs[5]:
    st.header("Live OCR Sourcing Agent")
    st.write(
        "Download and run the desktop OCR agent alongside your browser. "
        "It will capture the listing area, extract VIN/price/mileage in real-time, "
        "send to the AI backend, and overlay deal scores on your screen."
    )
    ocr_code = '''# ocr_agent.py
import time
import re
import threading
import requests
from PIL import ImageGrab
import pytesseract
import tkinter as tk
from tkinter import ttk

# Configuration
CAPTURE_REGION = (0, 100, 1920, 1080)
OCR_LANG = 'eng'
SCORING_API_URL = 'https://your-streamlit-app.com/api/score_listing'
POLL_INTERVAL = 5

VIN_PATTERN = r"\b([A-HJ-NPR-Z0-9]{17})\b"
PRICE_PATTERN = r"\$\s*([0-9,]+(?:\.[0-9]{1,2})?)"
MILEAGE_PATTERN = r"([0-9,]+)\s*mi"

class Overlay(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.8)
        self.label = ttk.Label(self, text='', background='black', foreground='white', font=('Arial', 12))
        self.label.pack(padx=10, pady=5)

    def show_message(self, msg: str, duration=5):
        self.label.config(text=msg)
        self.update_idletasks()
        self.after(duration * 1000, self.clear)

    def clear(self):
        self.label.config(text='')

overlay = Overlay()
seen = set()

def capture_screen(region=None):
    return ImageGrab.grab(bbox=region)

def ocr_image(img):
    return pytesseract.image_to_string(img, lang=OCR_LANG)

def parse_listings(text):
    vins = re.findall(VIN_PATTERN, text)
    prices = re.findall(PRICE_PATTERN, text)
    miles = re.findall(MILEAGE_PATTERN, text)
    listings = []
    for i, vin in enumerate(vins):
        price = float(prices[i].replace(',', '')) if i < len(prices) else None
        mileage = int(miles[i].replace(',', '')) if i < len(miles) else None
        listings.append({'vin': vin, 'price': price, 'mileage': mileage})
    return listings

def score_listing(listing):
    try:
        resp = requests.post(SCORING_API_URL, json=listing, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {'error': str(e)}

def monitor_loop():
    while True:
        img = capture_screen(CAPTURE_REGION)
        text = ocr_image(img)
        listings = parse_listings(text)
        for lst in listings:
            key = (lst['vin'], lst.get('price'), lst.get('mileage'))
            if key not in seen:
                seen.add(key)
                result = score_listing(lst)
                if 'score' in result:
                    msg = f"VIN {lst['vin']} → Score {result['score']} Profit ${result.get('estimated_profit',0)}"
                else:
                    msg = f"Scoring error: {result.get('error')}"
                overlay.show_message(msg)
        time.sleep(POLL_INTERVAL)

threading.Thread(target=monitor_loop, daemon=True).start()
overlay.mainloop()'''
    st.download_button(
        label="Download OCR Agent (ocr_agent.py)",
        data=ocr_code,
        file_name="ocr_agent.py",
        mime="text/x-python"
    )
    st.markdown("**Instructions:**")
    st.markdown("""
1. Install dependencies:
   ```bash
   pip install pytesseract pillow opencv-python requests
   sudo apt install tesseract-ocr
   ```
2. Adjust `CAPTURE_REGION` in `ocr_agent.py` to match your browser.
3. Run:
   ```bash
   python ocr_agent.py
   ```
4. Browse auction sites; overlay will show live deal scores.
""")
