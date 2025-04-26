```python
# app.py

"""
AutoIntel.AI Car Intelligence Dashboard
Refactored to ensure AI Assistant uses its own GPT calls and avoid code-review errors in that tab.
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
    key = (
        st.secrets.get("openai", {}).get("api_key", "")
        or os.getenv("OPENAI_API_KEY", "")
    )
    if not key:
        st.error("❌ OpenAI API key missing. Set OPENAI_API_KEY in secrets or env.")
        st.stop()
    return key

# ------------------------------------------------------------
# 3. LOGGING SETUP
# ------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    features: List[str] = Field(default_factory=list)

# ------------------------------------------------------------
# 5. LISTING GENERATOR
# ------------------------------------------------------------
class ListingGenerator:
    def __init__(self, config: AppConfig):
        self.config = config

    def generate_listing(self, index: int) -> CarListing:
        make = random.choice(list(self.config.MAKES_MODELS.keys()))
        model = random.choice(self.config.MAKES_MODELS[make])
        year = random.randint(self.config.MIN_YEAR, self.config.MAX_YEAR)
        price = round(random.uniform(self.config.MIN_PRICE, self.config.MAX_PRICE), 2)
        mileage = random.randint(0, 200_000)
        location = random.choice(self.config.LOCATIONS)
        return CarListing(id=index, make=make, model=model, year=year, price=price, mileage=mileage, location=location)

    def generate_listings(self, count: int) -> List[CarListing]:
        if count < 1:
            raise ValueError("Count must be positive.")
        return [self.generate_listing(i) for i in range(1, count + 1)]

# ------------------------------------------------------------
# 6. VIN DECODER
# ------------------------------------------------------------
@st.cache_data(ttl=3600)
def decode_vin(vin: str, year: Optional[int] = None) -> Dict[str, object]:
    vin = vin.strip() if isinstance(vin, str) else ""
    if len(vin) != 17:
        raise ValueError("VIN must be 17 characters.")
    params = {"format": AppConfig.NHTSA_FORMAT}
    if year and year >= AppConfig.MIN_YEAR:
        params["modelyear"] = year
    resp = requests.get(AppConfig.NHTSA_DECODE_URL + vin, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

# ------------------------------------------------------------
# 7. AI REVIEWER
# ------------------------------------------------------------
class AIReviewer:
    def __init__(self, model: str, api_key: str):
        openai.api_key = api_key
        self.model = model

    def review_code(self, code: str) -> str:
        if not code.strip():
            raise ValueError("No code provided.")
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role":"user","content":f"Review this code:```\n{code}\n```"}]
        )
        return response.choices[0].message.content.strip()

# ------------------------------------------------------------
# 8. AI ASSISTANT
# ------------------------------------------------------------
def get_ai_assistant_response(prompt: str) -> str:
    if not prompt.strip():
        return "Please ask a question."
    low = prompt.lower()
    if "price" in low:
        return "Prices update often—see Track Listings."  
    if "mileage" in low:
        return "Lower mileage often means higher value."  
    resp = openai.ChatCompletion.create(model=AppConfig.OPENAI_MODEL, messages=[{"role":"user","content":prompt}])
    return resp.choices[0].message.content.strip()

# ------------------------------------------------------------
# 9. UI & MAIN
# ------------------------------------------------------------
def main():
    st.title("AutoIntel.AI Car Intelligence Dashboard")
    config = AppConfig()
    api_key = get_openai_api_key()
    generator = ListingGenerator(config)
    reviewer = AIReviewer(config.OPENAI_MODEL, api_key)

    tabs = st.tabs(["Track Listings","AI Assistant","VIN Decoder","Deal Alerts","Self-Enhancement"])

    with tabs[0]:
        count = st.number_input("Listings count",1,50,config.LISTINGS_DEFAULT_COUNT)
        if st.button("Generate Listings"):
            st.write(generator.generate_listings(count))

    with tabs[1]:
        q = st.text_input("Ask:")
        if st.button("Ask AI", key="ask"): st.write(get_ai_assistant_response(q))

    with tabs[2]:
        vin=st.text_input("VIN:")
        y=st.number_input("Year opt",0,config.MAX_YEAR,0)
        y=None if y<config.MIN_YEAR else y
        if st.button("Decode VIN"): st.json(decode_vin(vin,y))

    with tabs[3]:
        sample=generator.generate_listings(5)
        opts=[f"{c.year} {c.make} {c.model} ${c.price}" for c in sample]
        sel=st.selectbox("Pick",opts)
        th=st.number_input("Max $",0.0,100000.0,0.0)
        if st.button("Chk"): st.success("Deal" if sample[opts.index(sel)].price<=th else "No deal")

    with tabs[4]:
        code=st.file_uploader("Upload",type=["py"]); text=code.read().decode() if code else st.text_area("Paste",height=200)
        if st.button("Analyze Code"): st.write(reviewer.review_code(text))

if __name__=="__main__": main()
```
