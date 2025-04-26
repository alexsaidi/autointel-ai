# app.py

import os
import logging
import random
import requests
import streamlit as st
import openai
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ------------------------------------------------------------
# 1. CONFIG & SECRETS
# ------------------------------------------------------------
st.set_page_config(page_title="AutoIntel.AI Car Dashboard", layout="wide")
# Load from Streamlit secrets or environment
OPENAI_API_KEY = st.secrets.get("openai", {}).get("api_key") or os.getenv("OPENAI_API_KEY", "")
VIN_API_BASE = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/"

# TODO: Add GitHub Actions workflow to run lint/test and deploy on merge to main
# TODO: Move all secrets into CI/CD-managed environment

# ------------------------------------------------------------
# 2. LOGGING SETUP
# ------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("AutoIntel.AI")

# ------------------------------------------------------------
# 3. DATA MODELS
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
# 4. DATA UTILITIES
# ------------------------------------------------------------
@st.cache_data(ttl=600)
def generate_listings(n: int = 5) -> List[CarListing]:
    """
    Simulate fetching n new car listings.
    """
    makes_models = {
        "Toyota": ["Camry", "Corolla"],
        "Honda": ["Civic", "Accord"],
        "Ford": ["Mustang", "F-150"],
        "BMW": ["3 Series", "X5"],
    }
    locations = ["NY, NY", "LA, CA", "Chicago, IL", "Houston, TX"]
    listings = []
    for i in range(1, n + 1):
        make = random.choice(list(makes_models.keys()))
        model = random.choice(makes_models[make])
        year = random.randint(2012, 2024)
        price = round(random.uniform(15000, 45000), 2)
        mileage = random.randint(5000, 120000)
        location = random.choice(locations)
        vin = f"{random.randint(10000000000000000, 99999999999999999):017d}"
        image_url = f"https://source.unsplash.com/featured/?{make},{model},car"
        listings.append(
            CarListing(
                id=i,
                make=make,
                model=model,
                year=year,
                price=price,
                mileage=mileage,
                location=location,
                vin=vin,
                image_url=image_url,
            )
        )
    logger.info("Generated %d listings", len(listings))
    return listings

@st.cache_data(ttl=3600)
def decode_vin(vin: str) -> VINDecodeResult:
    """
    Decode VIN via NHTSA API.
    """
    try:
        resp = requests.get(f"{VIN_API_BASE}{vin}?format=json", timeout=10)
        resp.raise_for_status()
        data = resp.json().get("Results", [{}])[0]
        result = VINDecodeResult(
            VIN=vin,
            Make=data.get("Make"),
            Model=data.get("Model"),
            ModelYear=data.get("ModelYear"),
            BodyClass=data.get("BodyClass"),
            Error=None,
        )
        logger.info("VIN %s decoded: %s", vin, result)
    except Exception as e:
        logger.error("VIN decode failed: %s", e)
        result = VINDecodeResult(VIN=vin, Make=None, Model=None, ModelYear=None, BodyClass=None, Error=str(e))
    return result

# ------------------------------------------------------------
# 5. AI UTILITIES
# ------------------------------------------------------------
@st.cache_resource
def get_openai_client():
    if not OPENAI_API_KEY:
        raise RuntimeError("OpenAI API key is missing.")
    openai.api_key = OPENAI_API_KEY
    return openai

def simple_keyword_response(text: str) -> Optional[str]:
    """
    Return a canned response if certain keywords found.
    """
    text = text.lower()
    if "price" in text:
        return "Price varies by region—check our listings tab for current numbers."
    if "mileage" in text:
        return "Lower mileage usually commands a higher price. Anything else you need?"
    if "hello" in text or "hi" in text:
        return "Hi! How can I assist with your car research today?"
    return None

def trim_history(history: List[Dict[str, str]], max_chars: int = 2000) -> List[Dict[str, str]]:
    """
    Trim oldest messages until under max_chars.
    """
    total = sum(len(m["content"]) for m in history)
    while total > max_chars and len(history) > 2:
        removed = history.pop(0)
        total = sum(len(m["content"]) for m in history)
        logger.debug("Trimmed message: %s", removed)
    return history

def ask_openai(history: List[Dict[str, str]]) -> str:
    """
    Query OpenAI ChatCompletion.
    """
    client = get_openai_client()
    trimmed = trim_history(history)
    try:
        resp = client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=trimmed,
            max_tokens=150,
        )
        answer = resp.choices[0].message.content.strip()
        logger.info("OpenAI replied: %s", answer)
        return answer
    except Exception as e:
        logger.error("OpenAI error: %s", e)
        return "Sorry, I couldn't process that right now."

def get_ai_response(user_msg: str, history: List[Dict[str, str]]) -> str:
    """
    Decide between keyword response or API call.
    """
    if resp := simple_keyword_response(user_msg):
        history.append({"role": "assistant", "content": resp})
        return resp

    history.append({"role": "user", "content": user_msg})
    reply = ask_openai(history)
    history.append({"role": "assistant", "content": reply})
    return reply

# ------------------------------------------------------------
# 6. UI COMPONENTS
# ------------------------------------------------------------
def display_metrics(listings: List[CarListing]):
    """
    Show average/high/low price metrics.
    """
    if not listings:
        st.warning("No listings to show metrics.")
        return
    avg = sum(l.price for l in listings) / len(listings)
    hi = max(listings, key=lambda l: l.price)
    lo = min(listings, key=lambda l: l.price)
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Price", f"${avg:,.0f}")
    c2.metric("Highest", f"${hi.price:,.0f}", f"{hi.year} {hi.make}")
    c3.metric("Lowest", f"${lo.price:,.0f}", f"{lo.year} {lo.make}")

def display_listing(listing: CarListing):
    """
    Render a single listing.
    """
    cols = st.columns([2, 4, 1, 1, 2])
    if listing.image_url:
        cols[0].image(listing.image_url, use_column_width=True)
    cols[1].markdown(f"**{listing.year} {listing.make} {listing.model}**")
    cols[2].write(f"${listing.price:,.0f}")
    cols[3].write(f"{listing.mileage:,} mi")
    cols[4].write(listing.location)

# ------------------------------------------------------------
# 7. APP LAYOUT & LOGIC
# ------------------------------------------------------------
st.title("🕵️‍♂️ AutoIntel.AI Car Intelligence Dashboard")
tabs = st.tabs(["Track Listings", "AI Assistant", "VIN Decoder", "Deal Alerts", "Self-Enhancement"])

# --- Track Listings ---
with tabs[0]:
    st.header("Track Listings")
    if "prev" not in st.session_state:
        st.session_state.prev = []
    if "current" not in st.session_state:
        st.session_state.current = generate_listings(5)

    if st.button("🔄 Refresh"):
        st.session_state.prev = st.session_state.current
        st.session_state.current = generate_listings(st.session_state.current.__len__())

    prev_ids = {c.id for c in st.session_state.prev}
    curr_ids = {c.id for c in st.session_state.current}
    new = [c for c in st.session_state.current if c.id not in prev_ids]
    sold = [c for c in st.session_state.prev if c.id not in curr_ids]

    display_metrics(st.session_state.current)
    st.subheader("Current Listings")
    for l in st.session_state.current:
        display_listing(l)

    if new:
        st.subheader("🆕 New Since Last")
        for l in new:
            display_listing(l)

    if sold:
        st.subheader("✅ Removed/Sold")
        for l in sold:
            display_listing(l)

# --- AI Assistant ---
with tabs[1]:
    st.header("AI Assistant")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "You are an expert car listings assistant."}
        ]
    user_q = st.text_input("Your question:")
    if st.button("Ask AI") and user_q:
        answer = get_ai_response(user_q, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**AI:** {msg['content']}")

# --- VIN Decoder ---
with tabs[2]:
    st.header("VIN Decoder")
    vin_in = st.text_input("Enter 17-char VIN:")
    if st.button("Decode VIN") and vin_in:
        result = decode_vin(vin_in.strip())
        st.subheader("Decoded Data")
        for k, v in result.dict().items():
            if v is not None:
                st.write(f"**{k}:** {v}")

# --- Deal Alerts ---
with tabs[3]:
    st.header("Deal Alerts")
    listings_for_alert = generate_listings(8)
    choices = [f"{l.year} {l.make} {l.model} — ${l.price:,.0f}" for l in listings_for_alert]
    sel = st.selectbox("Select Listing:", choices)
    threshold = st.number_input("Max price you want ($):", min_value=0.0, step=500.0)
    if st.button("Check Deal"):
        idx = choices.index(sel)
        chosen = listings_for_alert[idx]
        if chosen.price <= threshold:
            st.success(f"🎉 Deal! {chosen.year} {chosen.make} at ${chosen.price:,.0f}")
        else:
            st.info(f"❌ No deal: this one is ${chosen.price:,.0f}")

# --- Self-Enhancement Suggestions ---
with tabs[4]:
    st.header("Self-Enhancement Suggestions")
    st.markdown("""
- **Monolithic but Structured:** Everything in one file, organized into sections.
- **Type Checking:** Models via Pydantic for validation and autocompletion.
- **Caching:** `@st.cache_data` & `@st.cache_resource` for performance.
- **Logging:** `logging` module to trace operations and errors.
- **AI Integration:** Keyword shortcuts + OpenAI ChatCompletion.
- **UI/UX:** Responsive columns, Unsplash images, clear metrics.
- **Testing TODO:** Add `pytest` tests for each section (data, AI, UI logic).
- **CI/CD TODO:** Hook up GitHub Actions with `flake8`, `mypy`, `pytest`, and deploy to Streamlit or other host.
- **Secrets TODO:** Move secrets into Streamlit secrets or environment variables.
""")
