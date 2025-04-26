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
OPENAI_API_KEY = (
    st.secrets.get("openai", {}).get("api_key")
    or os.getenv("OPENAI_API_KEY", "")
)
VIN_API_BASE = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/"

# TODO: Add GitHub Actions workflow to run lint/tests and deploy on merge
# TODO: Move all secrets into CI/CD-managed environment

# ------------------------------------------------------------
# 2. LOGGING
# ------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("AutoIntelAI")

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
    makes_models = {
        "Toyota": ["Camry", "Corolla"],
        "Honda": ["Civic", "Accord"],
        "Ford": ["Mustang", "F-150"],
        "BMW": ["3 Series", "X5"],
    }
    locations = ["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX"]
    listings: List[CarListing] = []
    for i in range(1, n + 1):
        make = random.choice(list(makes_models.keys()))
        model = random.choice(makes_models[make])
        year = random.randint(2012, 2024)
        price = round(random.uniform(15000, 45000), 2)
        mileage = random.randint(5000, 120000)
        location = random.choice(locations)
        vin = f"{random.randint(10**16, 10**17-1):017d}"
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
        logger.info("Decoded VIN %s: %s", vin, result)
    except Exception as e:
        logger.error("VIN decode error for %s: %s", vin, e)
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
    t = text.lower()
    if "price" in t:
        return "Prices fluctuate—check the Listings tab for up-to-date figures."
    if "mileage" in t:
        return "Mileage impacts value. Lower mileage typically means higher price."
    if "hello" in t or "hi" in t:
        return "Hi there! How can I help you with car listings?"
    return None


def trim_history(history: List[Dict[str, str]], max_chars: int = 2000) -> List[Dict[str, str]]:
    total = sum(len(m["content"]) for m in history)
    while total > max_chars and len(history) > 2:
        removed = history.pop(0)
        total = sum(len(m["content"]) for m in history)
        logger.debug("Trimmed message: %s", removed)
    return history


def ask_openai(history: List[Dict[str, str]]) -> str:
    client = get_openai_client()
    trimmed = trim_history(history)
    try:
        resp = client.ChatCompletion.create(
            model="gpt-4",  # or "gpt-4-turbo"
            messages=trimmed,
            max_tokens=250,
            temperature=0.5,
        )
        reply = resp.choices[0].message.content.strip()
        logger.info("OpenAI reply: %s", reply)
        return reply
    except Exception as e:
        logger.error("OpenAI error: %s", e)
        return "Error: could not get response from AI."


def get_ai_response(user_msg: str, history: List[Dict[str, str]]) -> str:
    if resp := simple_keyword_response(user_msg):
        history.append({"role": "assistant", "content": resp})
        return resp
    history.append({"role": "user", "content": user_msg})
    reply = ask_openai(history)
    history.append({"role": "assistant", "content": reply})
    return reply


# ------------------------------------------------------------
# 6. UI HELPERS
# ------------------------------------------------------------
def display_metrics(listings: List[CarListing]):
    if not listings:
        st.warning("No listings available.")
        return
    avg = sum(l.price for l in listings) / len(listings)
    hi = max(listings, key=lambda l: l.price)
    lo = min(listings, key=lambda l: l.price)
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Price", f"${avg:,.0f}")
    c2.metric("Highest", f"${hi.price:,.0f}", f"{hi.year} {hi.make}")
    c3.metric("Lowest", f"${lo.price:,.0f}", f"{lo.year} {lo.make}")


def display_listing(listing: CarListing):
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
st.title("🕵️ AutoIntel.AI Car Intelligence Dashboard")
tabs = st.tabs(["Track Listings", "AI Assistant", "VIN Decoder", "Deal Alerts", "Self-Enhancement"])

# --- Track Listings ---
with tabs[0]:
    st.header("Track Listings")
    if "prev_listings" not in st.session_state:
        st.session_state.prev_listings = []
    if "current_listings" not in st.session_state:
        st.session_state.current_listings = generate_listings(5)

    if st.button("🔄 Refresh Listings"):
        st.session_state.prev_listings = st.session_state.current_listings
        st.session_state.current_listings = generate_listings(len(st.session_state.current_listings))

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

# --- AI Assistant ---
with tabs[1]:
    st.header("AI Assistant")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "You are an expert car listings assistant."}
        ]
    user_q = st.text_input("Enter your question:")
    if st.button("Ask AI") and user_q:
        reply = get_ai_response(user_q, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**AI:** {msg['content']}")

# --- VIN Decoder ---
with tabs[2]:
    st.header("VIN Decoder")
    vin_in = st.text_input("Enter a 17-character VIN:")
    if st.button("Decode VIN") and vin_in.strip():
        result = decode_vin(vin_in.strip())
        st.subheader("Decoded VIN Information")
        for key, val in result.dict().items():
            if val is not None:
                st.write(f"**{key}:** {val}")

# --- Deal Alerts ---
with tabs[3]:
    st.header("Deal Alerts")
    sample = generate_listings(8)
    choices = [f"{l.year} {l.make} {l.model} — ${l.price:,.0f}" for l in sample]
    sel = st.selectbox("Choose a listing:", choices)
    threshold = st.number_input("Your max price ($):", min_value=0.0, step=500.0)
    if st.button("Check Deal"):
        idx = choices.index(sel)
        chosen = sample[idx]
        if chosen.price <= threshold:
            st.success(f"🎉 Deal! {chosen.year} {chosen.make} at ${chosen.price:,.0f}")
        else:
            st.info(f"❌ No deal: it's ${chosen.price:,.0f}")

# --- Self-Enhancement ---
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
                with st.spinner("Reviewing code with GPT-4..."):
                    client = get_openai_client()
                    prompt = (
                        "You are an expert Python code reviewer. Analyze the following code and provide:\n"
                        "1. Maintainability score (1-10) and Performance score (1-10).\n"
                        "2. A bullet-point list of code quality suggestions.\n"
                        "3. Specific comments on caching, modularization, type hints, error handling, logging, and testing readiness.\n"
                        "4. (Optional) Improved code snippets or diff-style recommendations.\n\n"
                        f"```python\n{code}\n```"
                    )
                    response = client.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant for code review."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.5,
                    )
                    review = response.choices[0].message.content.strip()

                # Parse first line for scores
                lines = review.splitlines()
                review_body = review
                if lines and "Maintainability" in lines[0] and "Performance" in lines[0]:
                    try:
                        parts = lines[0].split(",")
                        m_score = parts[0].split(":")[1].strip()
                        p_score = parts[1].split(":")[1].strip()
                        st.subheader("Review Scores")
                        c1, c2 = st.columns(2)
                        c1.metric("Maintainability", m_score)
                        c2.metric("Performance", p_score)
                        review_body = "\n".join(lines[1:]).strip()
                    except Exception:
                        review_body = review

                st.subheader("Suggestions & Details")
                st.markdown(review_body)

                # Display diff/code blocks if present
                if "```diff" in review_body:
                    diff = review_body.split("```diff", 1)[1].rsplit("```", 1)[0]
                    st.subheader("Code Diff Suggestions")
                    st.code(diff, language="diff")
                elif "```python" in review_body:
                    snippets = review_body.split("```python")[1:]
                    for i, snip in enumerate(snippets):
                        code_snip = snip.rsplit("```", 1)[0]
                        st.subheader(f"Code Snippet {i+1}")
                        st.code(code_snip, language="python")

            except Exception as e:
                st.error(f"Error during code review: {e}")
