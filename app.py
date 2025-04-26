# app.py - AutoIntel.AI Car Intelligence Dashboard

import streamlit as st
import openai
import requests
import pandas as pd

# Page configuration
st.set_page_config(page_title="AutoIntel.AI", layout="wide")

def init_state():
    """
    Initialize Streamlit session state variables for listings, previous listings, deal alerts, and other necessary data.
    """
    if 'listings' not in st.session_state:
        st.session_state.listings = []
    if 'previous_listings' not in st.session_state:
        st.session_state.previous_listings = []
    if 'deal_alerts' not in st.session_state:
        st.session_state.deal_alerts = []  # list of criteria dicts
    if 'ai_history' not in st.session_state:
        st.session_state.ai_history = []

def check_openai_key():
    """
    Check for OpenAI API key in Streamlit secrets or environment.
    """
    try:
        if "openai_api_key" in st.secrets:
            openai.api_key = st.secrets["openai_api_key"]
        elif "OPENAI_API_KEY" in __import__("os").environ:
            openai.api_key = __import__("os").environ["OPENAI_API_KEY"]
        else:
            openai.api_key = None
    except Exception:
        openai.api_key = None

    if not openai.api_key:
        st.warning("OpenAI API key is not set. AI features will be disabled.")

def chatgpt_completion(system_prompt, user_prompt, temperature=0.3, max_tokens=150):
    """
    Make a call to OpenAI ChatCompletion API with given system and user prompt.
    Returns the assistant's response or None if API key missing or error.
    """
    if not openai.api_key:
        st.warning("OpenAI API key not available.")
        return None
    try:
        with st.spinner("AI is thinking..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"OpenAI API error: {e}")
        return None

def decode_vin(vin):
    """
    Decode a VIN using the NHTSA API and return a dictionary of vehicle data.
    """
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json"
    try:
        with st.spinner("Decoding VIN..."):
            res = requests.get(url, timeout=10)
        data = res.json()
        if "Results" in data and data["Results"]:
            results = data["Results"][0]
            # Extract common fields
            return {
                "Make": results.get("Make", "").title(),
                "Model": results.get("Model", "").title(),
                "Year": results.get("ModelYear", ""),
                "BodyClass": results.get("BodyClass", ""),
                "VehicleType": results.get("VehicleType", ""),
                "EngineCylinders": results.get("EngineCylinders", ""),
                "EngineHP": results.get("EngineHP", ""),
                "FuelTypePrimary": results.get("FuelTypePrimary", ""),
            }
        else:
            st.error("Invalid response from VIN decoder.")
            return None
    except requests.RequestException as e:
        st.error(f"Error contacting VIN decoding service: {e}")
        return None

def filter_listings_by_query(listings, query):
    """
    Filter listings based on query keywords. 
    Returns a subset of listings that match query terms in make, model, or body class.
    """
    if not query or not listings:
        return listings
    query = query.lower()
    relevant = []
    for lst in listings:
        text = f"{lst.get('Make','')} {lst.get('Model','')} {lst.get('BodyClass','')} {lst.get('Year','')} {lst.get('Price','')}"
        if all(term in text.lower() for term in query.split()):
            relevant.append(lst)
    return relevant

def summarize_changes(old_listings, new_listings):
    """
    Summarize differences between old and new listings using ChatGPT.
    """
    old_ids = {lst.get("VIN", lst.get("Link", "")) for lst in old_listings}
    new_ids = {lst.get("VIN", lst.get("Link", "")) for lst in new_listings}
    added_ids = new_ids - old_ids
    removed_ids = old_ids - new_ids

    added = [lst for lst in new_listings if lst.get("VIN", lst.get("Link", "")) in added_ids]
    removed = [lst for lst in old_listings if lst.get("VIN", lst.get("Link", "")) in removed_ids]

    changes_text = ""
    if added:
        changes_text += "Added listings:\n"
        for lst in added:
            changes_text += f"- {lst.get('Year','')} {lst.get('Make','')} {lst.get('Model','')} at ${lst.get('Price','')}\n"
    if removed:
        changes_text += "Removed listings:\n"
        for lst in removed:
            changes_text += f"- {lst.get('Year','')} {lst.get('Make','')} {lst.get('Model','')} that was ${lst.get('Price','')}\n"

    if not changes_text:
        changes_text = "No changes in listings."

    summary = chatgpt_completion(
        system_prompt="You summarize changes in car listings in one short paragraph or bullet points.",
        user_prompt=changes_text,
        max_tokens=60
    )
    if summary:
        return summary
    else:
        return changes_text.strip()

# Initialize state and API keys
init_state()
check_openai_key()

# App Title
st.title("AutoIntel.AI Car Intelligence Dashboard")

# Tabs for different functionalities
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Track Listings", 
    "💬 AI Assistant", 
    "🔍 VIN Decoder",
    "🚨 Deal Alerts",
    "🛠️ Self-Enhancement"
])

# 📈 Track Listings Tab
with tab1:
    st.header("Track Listings")
    st.subheader("Add New Listing")
    with st.form("add_listing_form", clear_on_submit=True):
        vin_input = st.text_input("VIN (optional)")
        price_input = st.number_input("Price (USD)", min_value=0, step=100)
        link_input = st.text_input("Listing URL (optional)")
        submitted = st.form_submit_button("Add Listing")
        
        if submitted:
            # Save previous state for summary
            st.session_state.previous_listings = st.session_state.listings.copy()
            listing = {}
            if vin_input:
                vin_data = decode_vin(vin_input.strip())
                if vin_data:
                    listing.update(vin_data)
                    listing["VIN"] = vin_input.strip()
                else:
                    st.error("Failed to decode VIN. Listing not added.")
                    listing = None
            else:
                listing = None
                st.error("VIN is required to add a listing.")
            
            if listing is not None:
                listing["Price"] = price_input
                listing["Link"] = link_input
                st.session_state.listings.append(listing)
                st.success("Listing added successfully!")
                # Show summary of changes
                summary = summarize_changes(st.session_state.previous_listings, st.session_state.listings)
                st.info(summary)
                # Display the newly added listing as a card-like element
                st.subheader("New Listing Added")
                cols = st.columns(3)
                with cols[0]:
                    st.markdown(f"**{listing.get('Year','')} {listing.get('Make','')} {listing.get('Model','')}**")
                    st.markdown(f"Price: ${listing.get('Price','')}")
                    if listing.get("Link"):
                        st.markdown(f"[View Listing]({listing.get('Link')})")
                    st.write("")  # spacer

    st.subheader("Filters & View Listings")
    filter_query = st.text_input("Smart Filter (e.g., 'SUV 25000')")
    filtered = filter_listings_by_query(st.session_state.listings, filter_query)
    if filtered:
        st.write(f"Displaying {len(filtered)} listing(s):")
        df = pd.DataFrame(filtered)
        st.dataframe(df)
    else:
        st.write("No listings to display. Add a listing above.")

    if st.session_state.listings:
        df_download = pd.DataFrame(st.session_state.listings)
        csv = df_download.to_csv(index=False)
        st.download_button(
            label="Download Listings as CSV",
            data=csv,
            file_name="listings.csv",
            mime="text/csv"
        )

# 💬 AI Assistant Tab
with tab2:
    st.header("AI Assistant")
    st.write("Ask questions about your listings.")
    query = st.text_input("Your question:")
    if st.button("Ask AI"):
        if not query:
            st.warning("Please enter a question before asking AI.")
        elif not st.session_state.listings:
            st.warning("No listings available to analyze.")
        else:
            relevant = filter_listings_by_query(st.session_state.listings, query)
            if relevant:
                listing_text = "\n".join(
                    f"- {lst.get('Year','')} {lst.get('Make','')} {lst.get('Model','')}, Price: ${lst.get('Price','')}"
                    for lst in relevant
                )
            else:
                listing_text = "No matching listings found."
            prompt = f"Here are some car listings:\n{listing_text}\n\nAnswer the question: {query}"
            answer = chatgpt_completion(
                system_prompt="You are a helpful assistant that answers questions about car listings given the listing data.",
                user_prompt=prompt,
                max_tokens=100
            )
            if answer:
                st.subheader("AI Assistant Response")
                st.write(answer)
            else:
                st.error("Failed to get response from AI.")

# 🔍 VIN Decoder Tab
with tab3:
    st.header("VIN Decoder")
    vin_input = st.text_input("Enter VIN to decode:")
    if st.button("Decode VIN"):
        if not vin_input:
            st.warning("Please enter a VIN.")
        else:
            data = decode_vin(vin_input.strip())
            if data:
                st.success("Decoded VIN information:")
                df = pd.DataFrame(list(data.items()), columns=["Field", "Value"])
                st.table(df)

# 🚨 Deal Alerts Tab
with tab4:
    st.header("Deal Alerts")
    st.write("Set criteria to get notified about matching new listings.")
    with st.form("deal_alert_form", clear_on_submit=True):
        alert_make = st.text_input("Make (optional)")
        alert_model = st.text_input("Model (optional)")
        alert_max_price = st.number_input("Max Price (0 = any)", min_value=0, step=1000)
        add_alert = st.form_submit_button("Add Alert")
        if add_alert:
            criterion = {"make": alert_make.title(), "model": alert_model.title(), "max_price": alert_max_price}
            st.session_state.deal_alerts.append(criterion)
            st.success("Alert criterion added!")
    if st.session_state.deal_alerts:
        st.write("### Current Alert Criteria:")
        for i, crit in enumerate(st.session_state.deal_alerts, start=1):
            m = crit["make"] or "Any"
            mo = crit["model"] or "Any"
            p = crit["max_price"] or "Any"
            st.write(f"{i}. Make: {m}, Model: {mo}, Max Price: {p}")
    if st.session_state.listings and st.session_state.deal_alerts:
        st.write("### Matching Listings for Alerts:")
        for crit in st.session_state.deal_alerts:
            matches = [
                lst for lst in st.session_state.listings
                if (not crit["make"] or lst.get("Make","") == crit["make"]) and
                   (not crit["model"] or lst.get("Model","") == crit["model"]) and
                   (crit["max_price"] == 0 or lst.get("Price", float('inf')) <= crit["max_price"])
            ]
            for m in matches:
                st.warning(f"⚠️ {m.get('Year','')} {m.get('Make','')} {m.get('Model','')} at ${m.get('Price','')} matches your alert criteria!")

# 🛠️ Self-Enhancement Tab
with tab5:
    st.header("Self-Enhancement")
    st.write("Suggestions to optimize and improve this application:")
    st.markdown("""
- **Modular Codebase:** Split logic into separate modules (e.g., `data_utils.py`, `api_utils.py`) for maintainability and easier testing.
- **Type Hinting and Linters:** Add type hints to functions and use a linter (e.g., flake8) to enforce code quality.
- **Caching:** Use `@st.cache_data` for expensive calls (e.g., VIN decoding) to speed up repeated operations.
- **Testing:** Implement unit tests (e.g., with `pytest`) to automatically verify functionality during development.
- **CI/CD:** Set up a CI/CD pipeline (e.g., GitHub Actions) to run tests and automatically deploy updates upon code changes.
- **Error Monitoring:** Integrate logging (e.g., Sentry) to monitor runtime errors and track issues in production.
- **Enhanced UI/UX:** Add real car images for listings, use custom CSS for card styling, and improve responsive design for mobile users.
""")
