import os
import json
import streamlit as st
import openai
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests

# ─── CONFIG ──────────────────────────────────────────────────────────────────────
openai.api_key = st.secrets["OPENAI_API_KEY"]  # set in .streamlit/secrets.toml
DATA_FILE = "listings.json"

# ─── PERSISTENCE ──────────────────────────────────────────────────────────────────
def load_saved_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def compare_data(old, new):
    old_urls = {item["url"] for item in old}
    new_urls = {item["url"] for item in new}
    added = [item for item in new if item["url"] not in old_urls]
    removed = [item for item in old if item["url"] not in new_urls]
    return added, removed

# ─── SCRAPER ─────────────────────────────────────────────────────────────────────
MARKET_URLS = {
    "autotrader":    "https://www.autotrader.com/cars-for-sale/all-cars/{term}",
    "cars.com":      "https://www.cars.com/shopping/results/?q={term}"
    # you can add more marketplaces here...
}

def fetch_listings(search_terms: list[str]) -> list[dict]:
    """
    For each term and each marketplace, spin up a headless browser,
    grab the page HTML, parse with BS4, and return a list of dicts:
      [{"source":..., "term":..., "title":..., "price":..., "url":...}, ...]
    """
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for term in search_terms:
            safe_term = term.replace(" ", "%20")
            for source, template in MARKET_URLS.items():
                url = template.format(term=safe_term)
                page.goto(url)
                page.wait_for_load_state("networkidle")
                html = page.content()
                soup = BeautifulSoup(html, "lxml")

                if source == "autotrader":
                    cards = soup.select(".inventory-listing")
                    for c in cards:
                        title_el = c.select_one(".inventory-listing-header .text-bold")
                        price_el = c.select_one(".first-price")
                        link_el  = c.select_one("a")
                        if not (title_el and price_el and link_el):
                            continue
                        results.append({
                            "source": source,
                            "term": term,
                            "title": title_el.get_text(strip=True),
                            "price": price_el.get_text(strip=True),
                            "url":   link_el["href"]
                        })

                elif source == "cars.com":
                    cards = soup.select(".vehicle-card")
                    for c in cards:
                        title_el = c.select_one(".title")
                        price_el = c.select_one(".primary-price")
                        link_el  = c.select_one("a")
                        if not (title_el and price_el and link_el):
                            continue
                        results.append({
                            "source": source,
                            "term": term,
                            "title": title_el.get_text(strip=True),
                            "price": price_el.get_text(strip=True),
                            "url":   link_el["href"]
                        })

                # Add other marketplaces here...
        browser.close()
    return results

# ─── AI UTILITIES ────────────────────────────────────────────────────────────────
def generate_summary(added, removed):
    prompt = f"""
New listings:
{json.dumps(added, indent=2)}

Sold listings:
{json.dumps(removed, indent=2)}

Provide a concise summary of what's changed—pricing trends, market conditions, and any notable observations.
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a car market analyst."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.7
    )
    return resp.choices[0].message.content

def ai_self_enhance():
    prompt = "Analyze this app's code and suggest optimizations and bug fixes."
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Python code optimization AI."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.7
    )
    return resp.choices[0].message.content

def get_vehicle_details(vin:str):
    try:
        r = requests.get(f'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json')
        data = r.json().get("Results", [])
        return data[0] if data else None
    except Exception as e:
        return {"Error": str(e)}

# ─── STREAMLIT UI ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="AutoIntel.AI", layout="wide")
st.title("🚘 AutoIntel.AI")

tabs = st.tabs(["📈 Track Listings", "💬 AI Assistant", "🔍 VIN Scanner", "🛠️ Self-Update"])

# — Track Listings —
with tabs[0]:
    st.header("Track Listings Across the Web")
    terms_input = st.text_input("Search terms (comma-separated)", "used cars NJ, trucks for sale")
    if st.button("🔄 Check Listings"):
        terms = [t.strip() for t in terms_input.split(",") if t.strip()]
        scraped = fetch_listings(terms)
        st.write(f"Fetched {len(scraped)} total listings.")

        saved = load_saved_data()
        added, removed = compare_data(saved, scraped)

        st.subheader("🆕 New Listings")
        st.write(f"Count: {len(added)}")
        st.json(added)

        st.subheader("💨 Sold / Removed Listings")
        st.write(f"Count: {len(removed)}")
        st.json(removed)

        if added or removed:
            summary = generate_summary(added, removed)
            st.markdown("### 🤖 AI Summary")
            st.write(summary)

        save_data(scraped)

# — AI Assistant —
with tabs[1]:
    st.header("Ask the AI Assistant")
    question = st.text_area("Your question about the market or listings:")
    if st.button("Ask"):
        if question:
            with st.spinner("Thinking..."):
                resp = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a car market expert."},
                        {"role": "user",   "content": question}
                    ],
                    temperature=0.7
                )
            st.markdown("**Answer:**")
            st.write(resp.choices[0].message.content)

# — VIN Scanner —
with tabs[2]:
    st.header("VIN Decoder")
    vin = st.text_input("Enter VIN:")
    if st.button("Decode VIN"):
        if vin:
            info = get_vehicle_details(vin)
            st.json(info)
        else:
            st.warning("Please enter a VIN.")

# — Self-Update —
with tabs[3]:
    st.header("Self-Enhancement Suggestions")
    if st.button("Run Self-Update"):
        with st.spinner("Analyzing code..."):
            suggestions = ai_self_enhance()
        st.markdown("### Suggestions")
        st.write(suggestions)
