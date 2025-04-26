# app.py

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
# 1. CONFIGURATION & CONSTANTS
# ------------------------------------------------------------
CONFIG = {
    "MIN_YEAR": 2012,
    "MAX_YEAR": 2024,
    "MIN_PRICE": 15000,
    "MAX_PRICE": 45000,
    "LISTINGS_DEFAULT_COUNT": 5,
    "VIN_API_BASE": "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/",
}

MAKES_MODELS = {
    "Toyota": ["Camry", "Corolla"],
    "Honda": ["Civic", "Accord"],
    "Ford": ["Mustang", "F-150"],
    "BMW": ["3 Series", "X5"],
}
LOCATIONS = ["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX"]

st.set_page_config(page_title="AutoIntel.AI Car Dashboard", layout="wide")
st.title("🕵️ AutoIntel.AI Car Intelligence Dashboard")

# ------------------------------------------------------------
# 2. SECRETS & EARLY EXIT
# ------------------------------------------------------------
def get_openai_api_key() -> str:
    """
    Fetch OpenAI API key from Streamlit secrets or environment.
    """
    return (
        st.secrets.get("openai", {}).get("api_key", "")
        or os.getenv("OPENAI_API_KEY", "")
    )

OPENAI_API_KEY = get_openai_api_key()
if not OPENAI_API_KEY:
    st.error("❌ OpenAI API key missing. Please configure OPENAI_API_KEY.")
    st.stop()

# ------------------------------------------------------------
# 3. LOGGING SETUP
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
    """Represents a car listing."""
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
    """Result of decoding a VIN."""
    VIN: str
    Make: Optional[str]
    Model: Optional[str]
    ModelYear: Optional[str]
    BodyClass: Optional[str]
    Error: Optional[str]

# ------------------------------------------------------------
# 5. DATA GENERATION & VIN DECODING
# ------------------------------------------------------------
def generate_listing(index: int) -> CarListing:
    """
    Generate a single random CarListing.
    """
    make = random.choice(list(MAKES_MODELS.keys()))
    model = random.choice(MAKES_MODELS[make])
    year = random.randint(CONFIG["MIN_YEAR"], CONFIG["MAX_YEAR"])
    price = round(random.uniform(CONFIG["MIN_PRICE"], CONFIG["MAX_PRICE"]), 2)
    mileage = random.randint(5000, 120000)
    location = random.choice(LOCATIONS)
    vin = f"{random.randint(10**16, 10**17 - 1):017d}"
    image_url = f"https://source.unsplash.com/featured/?{make},{model},car"
    listing = CarListing(
        id=index,
        make=make,
        model=model,
        year=year,
        price=price,
        mileage=mileage,
        location=location,
        vin=vin,
        image_url=image_url,
    )
    logger.debug("Generated listing: %s", listing)
    return listing

@st.cache_data(ttl=600)
def generate_listings(count: int = CONFIG["LISTINGS_DEFAULT_COUNT"]) -> List[CarListing]:
    """
    Generate multiple random car listings.
    """
    return [generate_listing(i) for i in range(1, count + 1)]

@st.cache_data(ttl=3600)
def decode_vin(vin: str) -> VINDecodeResult:
    """
    Decode a VIN using the NHTSA API.
    Raises HTTPError on failure.
    """
    url = f"{CONFIG['VIN_API_BASE']}{vin}?format=json"
    resp = requests.get(url, timeout=10)
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
    logger.info("Decoded VIN %s: %s", vin, result)
    return result

# ------------------------------------------------------------
# 6. AI UTILITIES (GPT-4)
# ------------------------------------------------------------
@st.cache_resource
def get_openai_client() -> OpenAI:
    """
    Instantiate and return the OpenAI client.
    """
    return OpenAI(api_key=OPENAI_API_KEY)

def simple_keyword_response(message: str) -> Optional[str]:
    """
    Return a canned response for basic keywords.
    """
    text = message.lower()
    if "price" in text:
        return "Prices change frequently—see the Listings tab for current data."
    if "mileage" in text:
        return "Mileage affects value; lower mileage usually means higher price."
    if any(greet in text for greet in ("hello", "hi")):
        return "Hello! How can I assist with your car listings today?"
    return None

def ask_openai(history: List[Dict[str, str]]) -> str:
    """
    Send the conversation history to GPT-4 and return the assistant's reply.
    """
    client = get_openai_client()
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=history,
            max_tokens=250,
            temperature=0.5,
        )
        reply = response.choices[0].message.content.strip()
        logger.info("OpenAI reply: %s", reply)
        return reply
    except Exception as err:
        logger.error("OpenAI API error: %s", err)
        return "⚠️ Sorry, I couldn't complete the code review right now."

def get_ai_response(user_input: str, history: List[Dict[str, str]]) -> str:
    """
    Get response for AI Assistant: check keywords, else call GPT-4.
    """
    if reply := simple_keyword_response(user_input):
        history.append({"role": "assistant", "content": reply})
        return reply

    history.append({"role": "user", "content": user_input})
    reply = ask_openai(history)
    history.append({"role": "assistant", "content": reply})
    return reply

# ------------------------------------------------------------
# 7. UI HELPERS
# ------------------------------------------------------------
def display_metrics(listings: List[CarListing]) -> None:
    """
    Show average, highest, and lowest price metrics.
    """
    if not listings:
        st.warning("No listings to display metrics.")
        return
    avg_price = sum(l.price for l in listings) / len(listings)
    highest = max(listings, key=lambda l: l.price)
    lowest = min(listings, key=lambda l: l.price)
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Price", f"${avg_price:,.0f}")
    c2.metric("Highest Price", f"${highest.price:,.0f}", f"{highest.year} {highest.make}")
    c3.metric("Lowest Price", f"${lowest.price:,.0f}", f"{lowest.year} {lowest.make}")

def display_listing(listing: CarListing) -> None:
    """
    Render a single CarListing in the Streamlit app.
    """
    cols = st.columns([2, 4, 1, 1, 2])
    if listing.image_url:
        cols[0].image(listing.image_url, use_column_width=True)
    cols[1].markdown(f"**{listing.year} {listing.make} {listing.model}**")
    cols[2].write(f"${listing.price:,.0f}")
    cols[3].write(f"{listing.mileage:,} mi")
    cols[4].write(listing.location)

# ------------------------------------------------------------
# 8. MAIN APP TABS & LOGIC
# ------------------------------------------------------------
tabs = st.tabs([
    "Track Listings",
    "AI Assistant",
    "VIN Decoder",
    "Deal Alerts",
    "Self-Enhancement"
])

# --- Track Listings ---
with tabs[0]:
    st.header("Track Listings")
    if "prev_listings" not in st.session_state:
        st.session_state.prev_listings = []
    if "current_listings" not in st.session_state:
        st.session_state.current_listings = generate_listings()

    if st.button("🔄 Refresh Listings"):
        st.session_state.prev_listings = st.session_state.current_listings
        count = len(st.session_state.current_listings)
        st.session_state.current_listings = generate_listings(count)

    prev_ids = {c.id for c in st.session_state.prev_listings}
    curr_ids = {c.id for c in st.session_state.current_listings}
    added = [c for c in st.session_state.current_listings if c.id not in prev_ids]
    removed = [c for c in st.session_state.prev_listings if c.id not in curr_ids]

    display_metrics(st.session_state.current_listings)
    st.subheader("Current Listings")
    for car in st.session_state.current_listings:
        display_listing(car)

    if added:
        st.subheader("🆕 New Since Last")
        for car in added:
            display_listing(car)
    if removed:
        st.subheader("✅ Removed/Sold")
        for car in removed:
            display_listing(car)

# --- AI Assistant ---
with tabs[1]:
    st.header("AI Assistant")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "You are an expert car listings assistant."}
        ]

    question = st.text_input("Ask the AI assistant a question:")
    if st.button("Ask AI") and question:
        ans = get_ai_response(question, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": ans})

    for msg in st.session_state.chat_history:
        speaker = "**You:**" if msg["role"] == "user" else "**AI:**"
        st.markdown(f"{speaker} {msg['content']}")

# --- VIN Decoder ---
with tabs[2]:
    st.header("VIN Decoder")
    vin_input = st.text_input("Enter a 17-character VIN:")
    if st.button("Decode VIN") and vin_input:
        try:
            vin_info = decode_vin(vin_input.strip())
            st.subheader("Decoded VIN Information")
            for field, val in vin_info.dict().items():
                if val is not None:
                    st.write(f"**{field}:** {val}")
        except requests.HTTPError as he:
            st.error(f"API error: {he}")

# --- Deal Alerts ---
with tabs[3]:
    st.header("Deal Alerts")
    sample = generate_listings(8)
    choices = [
        f"{c.year} {c.make} {c.model} — ${c.price:,.0f}" for c in sample
    ]
    selection = st.selectbox("Select a listing:", choices)
    threshold = st.number_input("Your max price ($):", min_value=0.0, step=500.0)
    if st.button("Check Deal"):
        idx = choices.index(selection)
        chosen = sample[idx]
        if chosen.price <= threshold:
            st.success(f"🎉 Good deal! {chosen.year} {chosen.make} at ${chosen.price:,.0f}")
        else:
            st.info(f"❌ No deal: it's ${chosen.price:,.0f}")

# --- Self-Enhancement ---
with tabs[4]:
    st.header("AI-Powered Code Review")
    uploaded_file = st.file_uploader("Upload a Python file", type=["py"])
    if uploaded_file:
        code_text = uploaded_file.read().decode("utf-8")
    else:
        code_text = st.text_area("Or paste your Python code here", height=200)

    if st.button("Analyze Code"):
        if not code_text.strip():
            st.warning("Please upload or paste some code first.")
        else:
            # Build the review prompt
            prompt = (
                "You are an expert Python code reviewer. Analyze the following code and provide:\n"
                "1. Maintainability score (1-10) and Performance score (1-10).\n"
                "2. A bullet-point list of code quality suggestions.\n"
                "3. Specific comments on caching, modularization, type hints, error handling, logging, and testing readiness.\n"
                "4. (Optional) Improved code snippets or diff-style recommendations.\n\n"
                f"```python\n{code_text}\n```"
            )
            with st.spinner("Reviewing with GPT-4..."):
                history = [
                    {"role": "system", "content": "You are a helpful assistant for code review."},
                    {"role": "user", "content": prompt},
                ]
                client = get_openai_client()
                review_resp = client.chat.completions.create(
                    model="gpt-4",
                    messages=history,
                    temperature=0.5,
                )
                review = review_resp.choices[0].message.content.strip()

            # Parse first line for scores
            lines = review.splitlines()
            body = review
            if lines and "Maintainability" in lines[0] and "Performance" in lines[0]:
                try:
                    m_part, p_part = lines[0].split(",")
                    m_score = m_part.split(":")[1].strip()
                    p_score = p_part.split(":")[1].strip()
                    st.subheader("Review Scores")
                    cm1, cm2 = st.columns(2)
                    cm1.metric("Maintainability", m_score)
                    cm2.metric("Performance", p_score)
                    body = "\n".join(lines[1:]).strip()
                except Exception:
                    body = review

            st.subheader("Suggestions & Details")
            st.markdown(body)

            # Render any diff or code snippet blocks
            if "```diff" in body:
                diff_text = body.split("```diff", 1)[1].rsplit("```", 1)[0]
                st.subheader("Code Diff Suggestions")
                st.code(diff_text, language="diff")
            elif "```python" in body:
                snippets = body.split("```python")[1:]
                for idx, snip in enumerate(snippets, start=1):
                    code_snip = snip.rsplit("```", 1)[0]
                    st.subheader(f"Suggested Snippet {idx}")
                    st.code(code_snip, language="python")
