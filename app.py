# ===== Imports =====
import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json

# Use Playwright for scraping dynamic sites
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# ===== Configuration and Initialization =====
st.set_page_config(page_title="AutoIntel.AI - Car Listings AI App", layout="wide")

# Title
st.title("🚗 AutoIntel.AI")

# Load OpenAI API key from Streamlit secrets
api_key = st.secrets.get("OPENAI_API_KEY", None)
if not api_key:
    st.error("OpenAI API key not found. Please add it to .streamlit/secrets.toml")
    st.stop()
# Initialize OpenAI client
openai_client = OpenAI(api_key=api_key)

# Data file path for storing listings
DATA_FILE = Path("listings.json")

# ===== Helper Functions =====

def scrape_market(make, model, year, zip_code, radius=50):
    """
    Scrapes car listings from a sample market website using Playwright and BeautifulSoup.
    Returns a list of listings (dictionaries) with keys: title, make, model, year, price, mileage, location, url.
    """
    listings = []
    if not PLAYWRIGHT_AVAILABLE:
        st.error("Playwright is not installed. Please install playwright to enable market scraping.")
        return listings

    try:
        # Construct search URL (example for illustrative purposes)
        search_query = f"{year} {make} {model}"
        url = f"https://www.autotrader.com/cars-for-sale/used-cars/{zip_code}?makeCodeList={make.upper()}&modelCodeList={model.capitalize()}&year={year}&searchRadius={radius}"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            html = page.content()
            browser.close()

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')
        # Example selectors (these will vary by actual site)
        listing_cards = soup.select("div.inventory-listing, div.listing")  # adjust as needed
        for card in listing_cards:
            try:
                title_tag = card.select_one("h2")
                price_tag = card.select_one("span.first-price")
                mileage_tag = card.select_one("div.item-card-specifications-mileage")
                location_tag = card.select_one("div.item-card-specifications-location")
                link_tag = card.select_one("a.listing-link")

                title = title_tag.get_text(strip=True) if title_tag else "Unknown"
                price = price_tag.get_text(strip=True) if price_tag else "N/A"
                # Clean price (remove $ and commas)
                price_val = None
                try:
                    price_val = int(price.replace("$", "").replace(",", "").split()[0])
                except:
                    price_val = None

                mileage_text = mileage_tag.get_text(strip=True) if mileage_tag else None
                mileage_val = None
                if mileage_text:
                    try:
                        mileage_val = int(mileage_text.replace("mi", "").replace(",", "").strip())
                    except:
                        mileage_val = None

                location = location_tag.get_text(strip=True) if location_tag else None
                link = link_tag['href'] if link_tag and link_tag.has_attr('href') else None
                if link and not link.startswith("http"):
                    link = "https://www.autotrader.com" + link

                # Parse year, make, model from title if possible
                parts = title.split()
                year_val, make_val, model_val = None, None, None
                if len(parts) >= 3:
                    try:
                        year_val = int(parts[0])
                        make_val = parts[1]
                        model_val = parts[2]
                    except:
                        pass

                listings.append({
                    "title": title,
                    "make": make_val or make,
                    "model": model_val or model,
                    "year": year_val or year,
                    "price": price_val,
                    "mileage": mileage_val,
                    "location": location,
                    "url": link
                })
            except Exception:
                # Skip listing if any parsing error occurs
                continue

    except Exception as e:
        st.error(f"Error scraping market data: {e}")
    return listings

def decode_vin(vin):
    """
    Decodes a VIN using NHTSA's public API.
    Returns a dictionary of vehicle information.
    """
    vin = vin.strip().upper()
    if len(vin) != 17:
        st.error("VIN must be 17 characters long.")
        return {}
    try:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
        response = requests.get(url, timeout=10)
        data = response.json()
        results = data.get("Results", [])
        info = {}
        for item in results:
            var = item.get("Variable", "")
            val = item.get("Value", "")
            if val and var:
                info[var] = val
        return info
    except Exception as e:
        st.error(f"Error decoding VIN: {e}")
        return {}

def ask_chat(messages, system_prompt="You are a helpful automotive assistant."):
    """
    Sends a list of message dicts (with 'role' and 'content') to OpenAI chat completion.
    Returns the assistant's reply content.
    """
    # Insert system prompt at beginning if not present
    if not any(msg.get("role") == "system" for msg in messages):
        messages = [{"role": "system", "content": system_prompt}] + messages
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        st.error(f"OpenAI API error: {e}")
        return ""

def estimate_price_with_market(listings, target_year, target_make, target_model, condition):
    """
    Estimates price based on scraped market data by filtering similar vehicles.
    """
    prices = []
    for car in listings:
        if car.get("year") == int(target_year) and car.get("make", "").lower() == target_make.lower() and car.get("model", "").lower() == target_model.lower():
            if car.get("price"):
                prices.append(car["price"])
    if prices:
        avg_price = sum(prices) / len(prices)
        # Adjust price based on condition (simple heuristic)
        if condition.lower() == "excellent":
            factor = 1.05
        elif condition.lower() == "good":
            factor = 1.0
        elif condition.lower() == "fair":
            factor = 0.95
        else:
            factor = 0.9
        return int(avg_price * factor), len(prices)
    return None, 0

# ===== Streamlit UI: Layout with Tabs =====
tabs = st.tabs(["Market Scraper", "VIN Decoder", "AI Q&A", "Car Comparison", "Price Estimator"])
tab_scraper, tab_vin, tab_qa, tab_compare, tab_price = tabs

# --- Market Scraper Tab ---
with tab_scraper:
    st.header("🚀 Market Listings Scraper")
    st.write("Search for car listings by make, model, year, and location.")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        make_input = st.text_input("Make (e.g. Honda)", value="Honda")
    with col2:
        model_input = st.text_input("Model (e.g. Civic)", value="Civic")
    with col3:
        year_input = st.text_input("Year (e.g. 2018)", value="2018")
    with col4:
        zip_input = st.text_input("Zip Code (e.g. 90210)", value="90210")
    radius_input = st.slider("Search Radius (miles)", min_value=10, max_value=100, value=50, step=5)
    if st.button("Search Listings"):
        if not (make_input and model_input and year_input and zip_input):
            st.error("Please fill in all search fields.")
        else:
            with st.spinner("Scraping market data..."):
                listings = scrape_market(make_input, model_input, year_input, zip_input, radius_input)
            if listings:
                # Save to session state and file
                st.session_state['last_listings'] = listings
                try:
                    with open(DATA_FILE, "w") as f:
                        json.dump(listings, f, indent=2)
                except Exception as e:
                    st.warning(f"Could not save listings to file: {e}")
                st.success(f"Found {len(listings)} listings. Displaying results:")
                # Display listings in table format
                for car in listings:
                    cols = st.columns((3, 1, 1, 2))
                    cols[0].markdown(f"[{car.get('title','')}]({car.get('url','')})")
                    cols[1].write(f"${car.get('price','N/A'):,}" if car.get('price') else "N/A")
                    cols[2].write(f"{car.get('mileage','N/A'):,} mi" if car.get('mileage') else "N/A")
                    cols[3].write(car.get('location',''))
            else:
                st.warning("No listings found or an error occurred during scraping.")

# --- VIN Decoder Tab ---
with tab_vin:
    st.header("🔍 VIN Decoder")
    st.write("Enter a 17-character Vehicle Identification Number to get vehicle details.")
    vin_input = st.text_input("VIN Number:", max_chars=17)
    if st.button("Decode VIN"):
        if not vin_input:
            st.error("Please enter a VIN.")
        else:
            with st.spinner("Decoding VIN..."):
                vin_info = decode_vin(vin_input)
            if vin_info:
                # Display key details
                st.subheader("Vehicle Information")
                info_table = {
                    "Make": vin_info.get("Make"),
                    "Model": vin_info.get("Model"),
                    "Year": vin_info.get("Model Year"),
                    "Engine": vin_info.get("Engine Model"),
                    "Manufacturer": vin_info.get("Manufacturer Name"),
                    "Vehicle Type": vin_info.get("Vehicle Type")
                }
                for key, val in info_table.items():
                    if val:
                        st.write(f"**{key}:** {val}")
            else:
                st.warning("Could not decode VIN or no data available.")

# --- AI Q&A Tab ---
with tab_qa:
    st.header("💬 AI Car Advisor (Q&A)")
    st.write("Ask any question about cars, and our AI will answer.")
    if 'qa_messages' not in st.session_state:
        st.session_state['qa_messages'] = [{"role": "system", "content": "You are a knowledgeable automotive assistant."}]
    # Display chat history
    for msg in st.session_state['qa_messages']:
        if msg["role"] in ["user", "assistant"]:
            st.chat_message(msg["role"]).write(msg["content"])
    # User input
    user_prompt = st.chat_input("Ask a question about cars or auto industry:")
    if user_prompt:
        st.session_state['qa_messages'].append({"role": "user", "content": user_prompt})
        with st.spinner("Generating answer..."):
            reply = ask_chat(st.session_state['qa_messages'], system_prompt="You are a knowledgeable automotive assistant.")
        if reply:
            st.session_state['qa_messages'].append({"role": "assistant", "content": reply})
            st.chat_message("assistant").write(reply)

# --- Car Comparison Tab ---
with tab_compare:
    st.header("⚖️ Car Comparison")
    st.write("Compare two vehicles and get an AI-powered summary of their differences.")
    comp_col1, comp_col2 = st.columns(2)
    with comp_col1:
        car1 = st.text_input("First Car (Year Make Model trim):", key="car1_input")
    with comp_col2:
        car2 = st.text_input("Second Car (Year Make Model trim):", key="car2_input")
    if st.button("Compare Cars"):
        if not car1 or not car2:
            st.error("Please enter both car descriptions.")
        else:
            prompt = f"Compare the following two cars: Car 1: {car1}. Car 2: {car2}. Discuss their strengths, weaknesses, and which might be a better choice overall."
            with st.spinner("Analyzing cars..."):
                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert car analyst."},
                        {"role": "user", "content": prompt}
                    ]
                )
                comparison = response.choices[0].message.content.strip()
            st.write(comparison)

# --- Price Estimator Tab ---
with tab_price:
    st.header("💰 Price Estimator")
    st.write("Estimate the fair market price of a car based on its specs and current listings.")
    price_col1, price_col2 = st.columns(2)
    with price_col1:
        est_year = st.text_input("Year:", key="year_est")
        est_make = st.text_input("Make:", key="make_est")
        est_model = st.text_input("Model:", key="model_est")
    with price_col2:
        est_mileage = st.number_input("Mileage:", min_value=0, step=1000, key="mileage_est")
        est_condition = st.selectbox("Condition:", ["Excellent", "Good", "Fair", "Poor"], key="cond_est")
        est_location = st.text_input("Location (City, State):", key="loc_est", value="New York, NY")
    if st.button("Estimate Price"):
        if not (est_year and est_make and est_model):
            st.error("Please provide year, make, and model.")
        else:
            est_year_int = int(est_year) if est_year.isdigit() else None
            # Try to use scraped data if available
            listings_data = st.session_state.get('last_listings', [])
            price = None
            count = 0
            if listings_data:
                price, count = estimate_price_with_market(listings_data, est_year, est_make, est_model, est_condition)
            if price:
                st.success(f"Estimated price based on {count} similar listings: ${price:,}")
            else:
                # Fallback to AI estimation
                prompt = f"Estimate the current market price of a {est_year} {est_make} {est_model} with {est_mileage} miles in {est_condition.lower()} condition in {est_location}."
                with st.spinner("Calculating estimation..."):
                    response = openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a knowledgeable car pricing assistant."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    ai_estimate = response.choices[0].message.content.strip()
                st.write(ai_estimate)
