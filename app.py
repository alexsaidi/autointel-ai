import streamlit as st
import requests
import openai
import pandas as pd

# Set your OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

# Apify JSON feed URL
DATA_URL = "https://api.apify.com/v2/datasets/MBcp5o14QqeeglnaS/items?clean=true&format=json"

# Load and process data
@st.cache_data
def load_data():
    response = requests.get(DATA_URL)
    data = response.json()
    df = pd.DataFrame(data)
    return df

# AI summary
def generate_summary(cars):
    car_text = "\n".join([f"- {car.get('title')} | ${car.get('price')}" for car in cars])
    prompt = f"Summarize the following car listings:\n{car_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Streamlit UI
st.title("🚗 AutoIntel.AI")
st.write("AI-powered car tracker and flipping insights")

df = load_data()
st.dataframe(df[['title', 'price', 'vin', 'location']].dropna())

if st.button("🔍 Summarize Listings with AI"):
    cars = df.to_dict(orient="records")
    with st.spinner("Thinking..."):
        summary = generate_summary(cars[:10])
    st.success("Done!")
    st.markdown(summary)
