"""
Streamlit Car Dashboard Application

This application allows users to generate mock car listings, decode VINs using NHTSA API,
and review code using OpenAI's GPT-4.
"""

import logging
from typing import List, Dict, Optional
import random
import requests
import streamlit as st
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppConfig:
    """Configuration class for application settings and constants."""
    # Year and price ranges for car listings
    MIN_YEAR: int = 1980
    MAX_YEAR: int = 2025
    MIN_PRICE: int = 1000
    MAX_PRICE: int = 100000

    # NHTSA API endpoints
    NHTSA_DECODE_URL: str = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/"
    NHTSA_FORMAT: str = "json"

    # OpenAI settings
    OPENAI_MODEL: str = "gpt-4"
    # Placeholder for OpenAI API Key. In production, set this from environment or secure storage.
    OPENAI_API_KEY: Optional[str] = None

    # Sample data for car listings
    MAKES_MODELS: Dict[str, List[str]] = {
        "Toyota": ["Camry", "Corolla", "RAV4", "Prius"],
        "Ford": ["F-150", "Mustang", "Explorer", "Focus"],
        "Honda": ["Civic", "Accord", "CR-V", "Fit"],
        "Tesla": ["Model S", "Model 3", "Model X", "Model Y"],
    }
    LOCATIONS: List[str] = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]


class ListingGenerator:
    """Generates mock car listings using configuration values."""

    def __init__(self, config: AppConfig):
        """
        Initialize the ListingGenerator with a given configuration.

        Args:
            config (AppConfig): Application configuration containing ranges and lists.
        """
        self.config = config

    def generate_listing(self) -> Dict[str, object]:
        """
        Generate a single mock car listing.

        Returns:
            dict: A dictionary representing a car listing.
        """
        make = random.choice(list(self.config.MAKES_MODELS.keys()))
        model = random.choice(self.config.MAKES_MODELS[make])
        year = random.randint(self.config.MIN_YEAR, self.config.MAX_YEAR)
        price = random.randint(self.config.MIN_PRICE, self.config.MAX_PRICE)
        location = random.choice(self.config.LOCATIONS)

        listing = {
            "make": make,
            "model": model,
            "year": year,
            "price": price,
            "location": location
        }
        logger.info(f"Generated listing: {listing}")
        return listing

    def generate_listings(self, count: int) -> List[Dict[str, object]]:
        """
        Generate a list of mock car listings.

        Args:
            count (int): Number of listings to generate.

        Returns:
            list: A list of car listing dictionaries.

        Raises:
            ValueError: If count is not a positive integer.
        """
        if count is None or count < 1:
            logger.error("Listing count must be a positive integer.")
            raise ValueError("Count must be a positive integer.")
        listings = [self.generate_listing() for _ in range(count)]
        logger.info(f"Generated {len(listings)} listings")
        return listings


class VinDecoder:
    """Handles VIN decoding by calling the NHTSA API."""

    @staticmethod
    @st.cache_data
    def decode_vin(vin: str, year: Optional[int] = None) -> Dict[str, object]:
        """
        Decode a vehicle's VIN using the NHTSA API.

        Args:
            vin (str): Vehicle Identification Number to decode.
            year (int, optional): Model year to assist in decoding.

        Returns:
            dict: Decoded VIN information as returned by the NHTSA API.

        Raises:
            ValueError: If VIN is invalid or not length 17.
            Exception: For network or API errors.
        """
        if not vin or not isinstance(vin, str):
            logger.error("VIN must be a non-empty string.")
            raise ValueError("VIN must be a non-empty string.")
        vin = vin.strip()
        if len(vin) != 17:
            logger.error(f"VIN length {len(vin)} is not equal to 17.")
            raise ValueError("VIN must be 17 characters long.")

        url = f"{AppConfig.NHTSA_DECODE_URL}{vin}?format={AppConfig.NHTSA_FORMAT}"
        if year:
            url += f"&modelyear={year}"

        logger.info(f"Decoding VIN: {vin} using URL: {url}")
        try:
            response = requests.get(url)
        except requests.RequestException as e:
            logger.exception("Failed to connect to NHTSA API.")
            raise Exception("Error connecting to NHTSA API.") from e

        if response.status_code != 200:
            logger.error(f"NHTSA API returned status code {response.status_code}")
            raise Exception(f"API request failed with status {response.status_code}")

        data = response.json()
        logger.info("VIN decoded successfully.")
        return data


class AIReviewer:
    """Integrates with OpenAI to review code using GPT-4."""

    def __init__(self, config: AppConfig):
        """
        Initialize the AIReviewer with a given configuration.

        Args:
            config (AppConfig): Application configuration with OpenAI settings.
        """
        self.config = config
        if self.config.OPENAI_API_KEY:
            openai.api_key = self.config.OPENAI_API_KEY

    def review_code(self, code: str) -> str:
        """
        Use GPT-4 to review the provided code snippet.

        Args:
            code (str): Code to be reviewed.

        Returns:
            str: Review comments from GPT-4.

        Raises:
            ValueError: If code is empty.
            Exception: For API or integration errors.
        """
        if not code or not code.strip():
            logger.error("Code to review is empty.")
            raise ValueError("No code provided for review.")

        logger.info("Sending code to GPT-4 for review.")
        try:
            response = openai.ChatCompletion.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": f"Please review this code and provide feedback:```\\n{code}\\n```"
                    }
                ]
            )
            review = response.choices[0].message.content.strip()
            logger.info("Received review from GPT-4.")
            return review
        except Exception as e:
            logger.exception("OpenAI API call failed.")
            raise Exception("Failed to get review from OpenAI.") from e


def main():
    st.title("Car Dashboard Application")
    config = AppConfig()
    listing_generator = ListingGenerator(config)
    vin_decoder = VinDecoder()  # static methods, config not needed for instantiation
    ai_reviewer = AIReviewer(config)

    st.sidebar.header("Configuration")
    st.sidebar.write("Configure your preferences here.")
    num_listings = st.sidebar.number_input(
        "Number of listings to generate",
        min_value=1, max_value=100, value=5
    )
    if st.sidebar.button("Generate Listings"):
        try:
            listings = listing_generator.generate_listings(num_listings)
            st.subheader("Generated Car Listings")
            st.write(listings)
        except ValueError as e:
            st.error(str(e))

    st.sidebar.markdown("---")
    st.subheader("VIN Decoder")
    vin_input = st.text_input("Enter VIN to decode")
    model_year = st.number_input(
        "Model Year (optional)",
        min_value=config.MIN_YEAR,
        max_value=config.MAX_YEAR,
        value=None
    )
    if st.button("Decode VIN"):
        try:
            decoded_data = vin_decoder.decode_vin(
                vin_input, year=model_year if model_year != 0 else None
            )
            st.json(decoded_data)
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error("Error decoding VIN: " + str(e))

    st.subheader("AI Code Reviewer")
    code_input = st.text_area("Paste code here to review")
    if st.button("Review Code"):
        try:
            review = ai_reviewer.review_code(code_input)
            st.write("**GPT-4 Review:**")
            st.write(review)
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error("Error during code review: " + str(e))


if __name__ == "__main__":
    main()
