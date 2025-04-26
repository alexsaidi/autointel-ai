# app.py

"""
AutoIntel.AI Car Intelligence Dashboard
Refactored with improved decode_vin and review_code methods,
secure API key handling, and correct Streamlit caching.
"""

import os
import logging
import random
from typing import List, Dict, Optional

import requests
import streamlit as st
import openai
from pydantic import BaseModel, Field

# ------------------------------------------------------------
# 1. CONFIGURATION & CONSTANTS
# ------------------------------------------------------------
class AppConfig:
    """Configuration values and constants."""
    MIN_YEAR: int = 1980
    MAX_YEAR: int = 2025
    MIN_PRICE: int = 1000
    MAX_PRICE: int = 100_000
    LISTINGS_DEFAULT_COUNT: int = 5

    NHTSA_DECODE_URL: str = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/"
    NHTSA_FORMAT: str = "json"

    OPENAI_MODEL: str = "gpt-4"

    MAKES_MODELS: Dict[str, List[str]] = {
        "Toyota": ["Camry", "Corolla", "RAV4", "Prius"],
        "Ford": ["F-150", "Mustang", "Explorer", "Focus"],
        "Honda": ["Civic", "Accord", "CR-V", "Fit"],
        "Tesla": ["Model S", "Model 3", "Model X", "Model Y"],
    }
    LOCATIONS: List[str] = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]


# ------------------------------------------------------------
# 2. SECRET MANAGEMENT
# ------------------------------------------------------------
def get_openai_api_key() -> str:
    """
    Fetch the OpenAI API key from Streamlit secrets or environment variables.
    """
    key = (
        st.secrets.get("openai", {}).get("api_key", "")
        or os.getenv("OPENAI_API_KEY", "")
    )
    if not key:
        st.error("❌ OpenAI API key is missing. Please set it in Streamlit secrets or as an environment variable.")
        st.stop()
    return key


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
    features: List[str] = Field(default_factory=list)


# ------------------------------------------------------------
# 5. LISTING GENERATOR
# ------------------------------------------------------------
class ListingGenerator:
    """Generates mock car listings."""

    def __init__(self, config: AppConfig):
        self.config = config

    def generate_listing(self, index: int) -> CarListing:
        """Generate a single random CarListing (no caching here)."""
        make = random.choice(list(self.config.MAKES_MODELS.keys()))
        model = random.choice(self.config.MAKES_MODELS[make])
        year = random.randint(self.config.MIN_YEAR, self.config.MAX_YEAR)
        price = round(random.uniform(self.config.MIN_PRICE, self.config.MAX_PRICE), 2)
        mileage = random.randint(0, 200_000)
        location = random.choice(self.config.LOCATIONS)
        return CarListing(
            id=index,
            make=make,
            model=model,
            year=year,
            price=price,
            mileage=mileage,
            location=location
        )

    @st.cache_data(ttl=600)
    def generate_listings(self, count: int) -> List[CarListing]:
        """Generate and cache a list of random CarListings."""
        if count < 1:
            raise ValueError("Count must be a positive integer.")
        return [self.generate_listing(i) for i in range(1, count + 1)]


# ------------------------------------------------------------
# 6. VIN DECODER
# ------------------------------------------------------------
class VinDecoder:
    """Decodes VIN numbers via the NHTSA API."""

    @staticmethod
    @st.cache_data(ttl=3600)
    def decode_vin(vin: str, year: Optional[int] = None) -> Dict[str, object]:
        """Decode a VIN using NHTSA, with parameterized requests."""
        vin = vin.strip() if isinstance(vin, str) else ""
        if len(vin) != 17:
            logger.error("VIN must be a 17-character string.")
            raise ValueError("VIN must be 17 characters long.")

        params = {"format": AppConfig.NHTSA_FORMAT}
        if year and year >= AppConfig.MIN_YEAR:
            params["modelyear"] = year

        try:
            resp = requests.get(
                AppConfig.NHTSA_DECODE_URL + vin,
                params=params,
                timeout=10
            )
            resp.raise_for_status()
        except requests.RequestException:
            logger.exception("Failed to connect to NHTSA API.")
            raise

        data = resp.json()
        logger.info("VIN decoded successfully.")
        return data


# ------------------------------------------------------------
# 7. AI REVIEWER
# ------------------------------------------------------------
class AIReviewer:
    """Uses OpenAI GPT-4 to review Python code."""

    def __init__(self, model: str, api_key: str):
        openai.api_key = api_key
        self.model = model

    def review_code(self, code: str) -> str:
        """Send code to GPT-4 and return its review."""
        if not code or not code.strip():
            logger.error("No code provided for review.")
            raise ValueError("Please provide code to review.")

        logger.info("Sending code to GPT-4 for review.")
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": (
                        "You are an expert Python code reviewer. "
                        "Analyze the following code and provide:\n"
                        "1. Maintainability score (1-10) and Performance score (1-10).\n"
                        "2. Bullet-point suggestions for improvement.\n"
                        "3. Specific comments on caching, modularization, type hints, error handling, logging, and testing.\n"
                        "4. (Optional) Code snippets or diff-style fixes.\n\n"
                        f"```python\n{code}\n```"
                    )
                }]
            )
            review = response.choices[0].message.content.strip()
            logger.info("Received review from GPT-4.")
            return review

        except Exception:
            logger.exception("OpenAI API call failed.")
            raise RuntimeError("Error during code review. Please check your API key and network.")


# ------------------------------------------------------------
# 8. STREAMLIT UI & MAIN
# ------------------------------------------------------------
def main():
    st.title("🕵️ AutoIntel.AI Car Intelligence Dashboard")

    # Load configuration and secrets
    config = AppConfig()
    api_key = get_openai_api_key()

    # Instantiate components
    generator = ListingGenerator(config)
    decoder = VinDecoder()
    reviewer = AIReviewer(model=config.OPENAI_MODEL, api_key=api_key)

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
        count = st.number_input(
            "Number of listings",
            min_value=1,
            max_value=50,
            value=config.LISTINGS_DEFAULT_COUNT,
            step=1
        )
        if st.button("Generate Listings"):
            try:
                listings = generator.generate_listings(count)
                st.write(listings)
            except ValueError as e:
                st.error(str(e))

    # --- AI Assistant (basic) ---
    with tabs[1]:
        st.header("AI Assistant")
        query = st.text_input("Ask about listings:")
        if st.button("Ask AI"):
            try:
                answer = reviewer.review_code(f"# Context question: {query}")
                st.write(answer)
            except Exception as e:
                st.error(str(e))

    # --- VIN Decoder ---
    with tabs[2]:
        st.header("VIN Decoder")
        vin = st.text_input("Enter a 17-character VIN:")
        year = st.number_input(
            "Model Year (optional)",
            min_value=0,
            max_value=config.MAX_YEAR,
            value=0,
            step=1
        )
        year = year if year >= config.MIN_YEAR else None
        if st.button("Decode VIN"):
            try:
                result = decoder.decode_vin(vin, year)
                st.json(result)
            except Exception as e:
                st.error(str(e))

    # --- Deal Alerts ---
    with tabs[3]:
        st.header("Deal Alerts")
        sample = generator.generate_listings(5)
        opts = [
            f"{c.year} {c.make} {c.model} — ${c.price:,.0f}"
            for c in sample
        ]
        choice = st.selectbox("Select listing:", opts)
        threshold = st.number_input("Max price ($):", min_value=0.0, step=500.0)
        if st.button("Check Deal"):
            sel = sample[opts.index(choice)]
            if sel.price <= threshold:
                st.success(f"Deal! {sel.make} at ${sel.price:,.0f}")
            else:
                st.info(f"No deal: ${sel.price:,.0f}")

    # --- Self-Enhancement / Code Review ---
    with tabs[4]:
        st.header("AI-Powered Code Review")
        uploaded = st.file_uploader("Upload a Python file", type=["py"])
        code_text = (
            uploaded.read().decode("utf-8")
            if uploaded
            else st.text_area("Or paste your Python code here", height=250)
        )

        if st.button("Analyze Code"):
            try:
                review = reviewer.review_code(code_text)
                # Parse first line for scores
                lines = review.splitlines()
                body = review
                if lines and "Maintainability" in lines[0] and "Performance" in lines[0]:
                    parts = lines[0].split(",")
                    m_score = parts[0].split(":")[1].strip()
                    p_score = parts[1].split(":")[1].strip()
                    c1, c2 = st.columns(2)
                    c1.metric("Maintainability", m_score)
                    c2.metric("Performance", p_score)
                    body = "\n".join(lines[1:]).strip()

                st.markdown(body)

                # Show diff or code blocks if present
                if "```diff" in body:
                    diff = body.split("```diff")[1].rsplit("```", 1)[0]
                    st.code(diff, language="diff")
                elif "```python" in body:
                    snippets = body.split("```python")[1:]
                    for idx, snip in enumerate(snippets, 1):
                        snippet = snip.rsplit("```", 1)[0]
                        st.code(snippet, language="python")

            except Exception as e:
                st.error(str(e))


if __name__ == "__main__":
