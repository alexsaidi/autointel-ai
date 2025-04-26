import streamlit as st
import requests
import json
import random
import openai
from typing import List, Dict, Any

# TODO: Add GitHub Actions CI/CD workflow (placeholder)

# Set page configuration and title
st.set_page_config(page_title="AutoIntel.AI Dashboard", layout="wide")
st.title("AutoIntel.AI Car Intelligence Dashboard")

# Initialize session state
if 'prev_listings' not in st.session_state:
    st.session_state['prev_listings'] = []
if 'current_listings' not in st.session_state:
    st.session_state['current_listings'] = []

# Cache data for VIN decoding to speed up repeated calls
@st.cache_data(ttl=3600)
def decode_vin_api(vin: str) -> Dict[str, Any]:
    """
    Call NHTSA API to decode a VIN. Returns result dictionary or empty if fail.
    """
    try:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
        res = requests.get(url, timeout=10)
        data = res.json()
        results = data.get("Results", [])
        if results:
            return results[0]
    except Exception:
        pass
    return {}

# Simulated data: possible car listings (would be fetched from real API in production)
ALL_LISTINGS = [
    {"id": 1, "title": "2018 Toyota Camry LE", "url": "https://www.example.com/listing/1", "image": "", "price": "$15,000", "mileage": "40,000 mi", "location": "New York, NY"},
    {"id": 2, "title": "2019 Honda Accord LX", "url": "https://www.example.com/listing/2", "image": "", "price": "$17,500", "mileage": "30,000 mi", "location": "Los Angeles, CA"},
    {"id": 3, "title": "2017 Ford F-150 XLT", "url": "https://www.example.com/listing/3", "image": "", "price": "$25,000", "mileage": "50,000 mi", "location": "Houston, TX"},
    {"id": 4, "title": "2020 BMW 3 Series 330i", "url": "https://www.example.com/listing/4", "image": "", "price": "$28,000", "mileage": "20,000 mi", "location": "Chicago, IL"},
    {"id": 5, "title": "2016 Chevrolet Malibu LT", "url": "https://www.example.com/listing/5", "image": "", "price": "$12,500", "mileage": "60,000 mi", "location": "Phoenix, AZ"},
    {"id": 6, "title": "2015 Mercedes-Benz C300", "url": "https://www.example.com/listing/6", "image": "", "price": "$18,000", "mileage": "70,000 mi", "location": "Philadelphia, PA"},
    {"id": 7, "title": "2018 Toyota Corolla SE", "url": "https://www.example.com/listing/7", "image": "", "price": "$13,000", "mileage": "35,000 mi", "location": "San Antonio, TX"},
    {"id": 8, "title": "2019 Honda Civic EX", "url": "https://www.example.com/listing/8", "image": "", "price": "$14,500", "mileage": "25,000 mi", "location": "San Diego, CA"},
    {"id": 9, "title": "2017 Ford Mustang GT", "url": "https://www.example.com/listing/9", "image": "", "price": "$26,000", "mileage": "45,000 mi", "location": "Dallas, TX"},
    {"id": 10, "title": "2020 Chevrolet Silverado 1500", "url": "https://www.example.com/listing/10", "image": "", "price": "$30,000", "mileage": "15,000 mi", "location": "San Jose, CA"}
]

def generate_new_listings(prev_listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Simulate fetching new listings: remove one random listing, add one new one.
    """
    if not prev_listings:
        # First fetch: return first 5 items
        return ALL_LISTINGS[:5]
    new_listings = prev_listings.copy()
    # Remove one random listing
    removed = random.choice(new_listings)
    new_listings.remove(removed)
    # Add one new listing not already in the list
    available = [item for item in ALL_LISTINGS if item not in new_listings]
    if available:
        added = random.choice(available)
        new_listings.append(added)
    return new_listings

# Ensure initial listings on first load
if not st.session_state['current_listings']:
    st.session_state['current_listings'] = generate_new_listings([])

# Create tabs for different functionalities
tabs = st.tabs(["Track Listings", "AI Assistant", "VIN Decoder", "Deal Alerts", "Self-Enhancement"])

# --- Track Listings Tab ---
with tabs[0]:
    st.header("Track Listings")
    st.write("Fetch the latest car listings and track changes over time.")
    # Button to refresh listings
    if st.button("Refresh Listings"):
        with st.spinner("Updating listings..."):
            prev = st.session_state['current_listings']
            new_list = generate_new_listings(prev)
            st.session_state['prev_listings'] = prev
            st.session_state['current_listings'] = new_list

    current_listings = st.session_state['current_listings']
    prev_listings = st.session_state['prev_listings']

    # Determine new vs sold listings
    new_items = []
    sold_items = []
    if prev_listings:
        prev_ids = {item['id'] for item in prev_listings}
        curr_ids = {item['id'] for item in current_listings}
        new_items = [item for item in current_listings if item['id'] not in prev_ids]
        sold_items = [item for item in prev_listings if item['id'] not in curr_ids]

    # Display metrics
    total = len(current_listings)
    delta = total - len(prev_listings) if prev_listings else 0
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Listings", total, delta)
    col2.metric("New Listings", len(new_items))
    col3.metric("Sold Listings", len(sold_items))

    # Display current listings
    if current_listings:
        st.subheader("Current Listings")
        for item in current_listings:
            cols = st.columns([1, 4, 2, 2, 2])
            # Optionally display image if URL is provided
            if item.get("image"):
                cols[0].image(item["image"], width=120)
            cols[1].markdown(f"**[{item['title']}]({item['url']})**")
            cols[2].write(item["price"])
            cols[3].write(item["mileage"])
            cols[4].write(item["location"])

    # Display newly listed items
    if new_items:
        st.subheader("Newly Listed Since Last Refresh")
        for item in new_items:
            cols = st.columns([1, 4, 2, 2, 2])
            if item.get("image"):
                cols[0].image(item["image"], width=120)
            cols[1].markdown(f"**[{item['title']}]({item['url']})**")
            cols[2].write(item["price"])
            cols[3].write(item["mileage"])
            cols[4].write(item["location"])

    # Display sold/removed items
    if sold_items:
        st.subheader("Recently Sold (Removed)")
        for item in sold_items:
            cols = st.columns([1, 4, 2, 2, 2])
            if item.get("image"):
                cols[0].image(item["image"], width=120)
            # Show struck-through title for removed items
            cols[1].markdown(f"~~{item['title']}~~")
            cols[2].write(item["price"])
            cols[3].write(item["mileage"])
            cols[4].write(item["location"])

# --- AI Assistant Tab ---
with tabs[1]:
    st.header("AI Assistant")
    st.write("Ask questions about the listings. Only a small subset of listings is sent to the AI to manage token size.")
    question = st.text_input("Enter your question for the AI assistant:", "")
    if st.button("Get AI Response"):
        if "OPENAI_API_KEY" not in st.secrets:
            st.error("OpenAI API key not found. Please set OPENAI_API_KEY in Streamlit secrets.")
        else:
            openai.api_key = st.secrets["OPENAI_API_KEY"]
            with st.spinner("Generating response..."):
                try:
                    # Filtering listings based on question
                    keywords = question.lower().split()
                    relevant = []
                    for item in st.session_state['current_listings']:
                        title_lower = item['title'].lower()
                        if any(kw in title_lower for kw in keywords):
                            relevant.append(item)
                    if relevant:
                        context_list = relevant[:5]
                    else:
                        # If no matching listings, use first 5
                        context_list = st.session_state['current_listings'][:5]
                    listings_text = "\n".join([json.dumps(item) for item in context_list])
                    messages = [
                        {"role": "system", "content": "You are an assistant specializing in car listings."},
                        {"role": "user", "content": f"Here are some recent car listings:\n{listings_text}\n\nQuestion: {question}"}
                    ]
                    response = openai.ChatCompletion.create(model="gpt-4", messages=messages, temperature=0.7)
                    answer = response.choices[0].message.content
                    st.write(answer)
                except openai.error.AuthenticationError:
                    st.error("Invalid OpenAI API key. Please check your key in Streamlit secrets.")
                except Exception as e:
                    st.error(f"An error occurred with the OpenAI API: {e}")

# --- VIN Decoder Tab ---
with tabs[2]:
    st.header("VIN Decoder")
    vin_input = st.text_input("Enter a 17-character VIN:", "")
    if st.button("Decode VIN"):
        vin = vin_input.strip()
        if len(vin) != 17:
            st.warning("Please enter a valid 17-character VIN.")
        else:
            with st.spinner("Decoding VIN..."):
                info = decode_vin_api(vin)
                if not info or not info.get("Make"):
                    st.error("No data found for this VIN or invalid VIN.")
                else:
                    # Display key fields in two columns
                    fields1 = ["Make", "Model", "ModelYear", "Trim", "BodyClass", "VehicleType"]
                    fields2 = ["EngineCylinders", "DisplacementL", "EngineHP", "FuelTypePrimary", "TransmissionStyle", "PlantCountry"]
                    colA, colB = st.columns(2)
                    for field in fields1:
                        if field in info and info[field]:
                            colA.write(f"**{field}:** {info[field]}")
                    for field in fields2:
                        if field in info and info[field]:
                            colB.write(f"**{field}:** {info[field]}")

# --- Deal Alerts Tab ---
with tabs[3]:
    st.header("Deal Alerts")
    st.info("Deal alerts functionality is under development. Check back soon!")

# --- Self-Enhancement Tab ---
with tabs[4]:
    st.header("Self-Enhancement Suggestions")
    st.write("Consider these optimizations to improve the app:")
    st.markdown("""
- **Modular Codebase:** Split logic into separate modules (e.g., `data_utils.py`, `api_utils.py`) for better maintainability.
- **Type Hinting and Linters:** Add type hints and use a linter (e.g., `flake8`) to enforce code quality.
- **Caching:** Use `@st.cache_data` for expensive operations (like VIN API calls) to speed up repeated use.
- **Testing:** Implement unit tests (e.g., with `pytest`) to automatically verify functionality during development.
- **CI/CD:** Use GitHub Actions to run tests and deploy updates on code changes.
- **Error Monitoring:** Integrate logging or an error tracking service (e.g., Sentry) to monitor runtime issues in production.
- **Enhanced UI/UX:** Include real car images for listings, improve styling (CSS/theming), and ensure responsive design for all device sizes.
""")
