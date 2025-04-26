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
    """Pydantic model for a single car listing."""
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
    """Pydantic model for VIN decoding results."""
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
    """Generate a single random CarListing."""
    make = random.choice(list(MAKES_MODELS.keys()))
    model = random.choice(MAKES_MODELS[make])
    year = random.randint(MIN_YEAR, MAX_YEAR)
    price = round(random.uniform(MIN_PRICE, MAX_PRICE), 2)
    mileage = random.randint(5000, 120000)
    location = random.choice(LOCATIONS)
    vin = f"{random.randint(10**16, 10**17 - 1):017d}"
    image_url = f"https://source.unsplash.com/featured/?{make},{model},car"
    listing = CarListing(
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
    logger.debug("Generated car: %s", listing)
    return listing

def generate_listings(n: int = LISTINGS_DEFAULT_COUNT) -> List[CarListing]:
    """
    Generate n random car listings.
    Splits logic into helper function for testability.
    """
    return [generate_random_car(i) for i in range(1, n + 1)]

@st.cache_data(ttl=3600)
def decode_vin(vin: str) -> VINDecodeResult:
    """
    Decode a vehicle VIN via NHTSA API.
    Raises on HTTP errors.
    """
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
    logger.info("Decoded VIN %s: %s", vin, result)
    return result

# ------------------------------------------------------------
# 6. AI UTILITIES (GPT-4)
# ------------------------------------------------------------
@st.cache_resource
def get_openai_client() -> OpenAI:
    """Instantiate and return the OpenAI client."""
    return OpenAI(api_key=OPENAI_API_KEY)

def simple_keyword_response(text: str) -> Optional[str]:
    """Return a canned reply for basic keywords."""
    t = text.lower()
    if "price" in t:
        return "Prices fluctuate—see the Listings tab for up-to-date figures."
    if "mileage" in t:
        return "Mileage impacts value—lower mileage often means higher price."
    if any(g in t for g in ("hello", "hi")):
        return "Hello! How can I assist you with car listings today?"
    return None

def ask_openai(history: List[Dict[str, str]]) -> str:
    """
    Send conversation history to GPT-4 and return the assistant's reply.
    Assumes history is already trimmed if needed.
    """
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=history,
        max_tokens=250,
        temperature=0.5,
    )
    reply = response.choices[0].message.content.strip()
    logger.info("OpenAI response: %s", reply)
    return reply

def get_ai_response(user_msg: str, history: List[Dict[str, str]]) -> str:
    """
    Get AI assistant response: uses simple keywords or falls back to GPT-4.
    Appends both user and assistant messages to history.
    """
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
    """Show average, highest, and lowest price metrics."""
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
    """Render a single CarListing as a Streamlit row with image."""
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
    "Self-Enhancement"
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
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

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

                # Parse scores
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

                # Show diffs or code snippets
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
