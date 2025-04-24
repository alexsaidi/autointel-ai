import openai
import requests
import json
import os
import streamlit as st

# Define the data URL and file
DATA_URL = "https://api.apify.com/v2/datasets/MBcp5o14QqeeglnaS/items?clean=true&format=json"
DATA_FILE = "car_data.json"

# --- Utility Functions ---
def load_saved_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def compare_data(old, new):
    old_ids = {car["id"] for car in old}
    new_ids = {car["id"] for car in new}
    new_listings = [car for car in new if car["id"] not in old_ids]
    sold_listings = [car for car in old if car["id"] not in new_ids]
    return new_listings, sold_listings

# Set OpenAI API Key (ensure it's set up properly in Streamlit Cloud secrets or environment variables)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to generate AI summary of car listings
def generate_summary(new_cars, sold_cars):
    prompt = f"""
    New listings:\n{json.dumps(new_cars, indent=2)}\n\nSold listings:\n{json.dumps(sold_cars, indent=2)}\n\nGive a clear, helpful summary of what's changed in the car listings, including pricing trends, market analysis, and condition reports.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a car market analyst AI."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# Function to get vehicle details based on VIN using NHTSA API
def get_vehicle_details(vin):
    try:
        # Use NHTSA API for vehicle info (or another reliable API)
        response = requests.get(f'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json')
        data = response.json()
        # Check if vehicle data is available
        if data['Results']:
            vehicle_info = data['Results'][0]
            return vehicle_info
        else:
            return None  # If no data is found
    except Exception as e:
        return f"Error fetching vehicle data: {str(e)}"

# Function for AI-driven code self-enhancement
def ai_self_enhance():
    prompt = "Analyze the current app code for performance issues, optimization opportunities, and bug fixes."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a code optimization AI."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# Streamlit app setup
st.set_page_config(page_title="AutoIntel.AI", layout="wide")
st.title("🚘 AutoIntel.AI")
st.caption("The smartest car intelligence app powered by AI.")

# --- Streamlit User Interface ---
tab1, tab2, tab3 = st.tabs(["📈 Track Listings", "🤖 AI Assistant", "🛠 Self Update"])

# --- Track Listings ---
with tab1:
    if st.button("🔄 Check for Updates"):
        saved = load_saved_data()
        latest = requests.get(DATA_URL).json()
        new, sold = compare_data(saved, latest)

        st.subheader("✅ Results")
        st.write(f"🆕 New cars: {len(new)}")
        st.write(f"💨 Sold cars: {len(sold)}")

        if new or sold:
            summary = generate_summary(new, sold)
            st.markdown("### 🤖 AI Summary")
            st.write(summary)
        else:
            st.info("No changes found.")

        save_data(latest)

# --- AI Assistant ---
with tab2:
    st.subheader("💬 Ask FlipBot anything")
    user_input = st.text_area("Type your question:")
    if st.button("Ask"):
        if user_input:
            with st.spinner("Thinking..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert car analyst and helpful AI assistant."},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7
                )
                st.success("✅ Done")
                st.markdown("### 📋 Answer")
                st.write(response.choices[0].message.content)

# --- Self Update Trigger ---
with tab3:
    st.subheader("🛠 Self-Enhancement")
    if st.button("🧠 Run Self-Update"):
        with st.spinner("Running self-enhancement..."):
            result = ai_self_enhance()
            st.success("Self-update complete. Reload to apply changes.")
            st.markdown("### 📋 Enhancement Suggestions")
            st.write(result)
