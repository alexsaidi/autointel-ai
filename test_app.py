import pytest
import requests
import openai

# Import classes from the app module
import app
from app import AppConfig, ListingGenerator, VinDecoder, AIReviewer

class DummyResponse:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data or {}

    def json(self):
        return self._data

def test_app_config_defaults():
    """Test default configuration values."""
    config = AppConfig()
    assert config.MIN_YEAR == 1980
    assert config.MAX_YEAR >= config.MIN_YEAR
    assert config.MIN_PRICE < config.MAX_PRICE
    assert "Toyota" in config.MAKES_MODELS
    assert isinstance(config.LOCATIONS, list)

def test_generate_listing_and_listings():
    """Test the ListingGenerator produces listings with correct keys and ranges."""
    config = AppConfig()
    generator = ListingGenerator(config)
    listing = generator.generate_listing()
    # Check that required keys exist
    assert set(listing.keys()) == {"make", "model", "year", "price", "location"}
    # Check year and price ranges
    assert config.MIN_YEAR <= listing["year"] <= config.MAX_YEAR
    assert config.MIN_PRICE <= listing["price"] <= config.MAX_PRICE
    # Generate multiple listings
    listings = generator.generate_listings(5)
    assert isinstance(listings, list)
    assert len(listings) == 5
    for item in listings:
        assert isinstance(item, dict)
    # Invalid count should raise ValueError
    with pytest.raises(ValueError):
        generator.generate_listings(0)

def test_vin_decoder_invalid_vin():
    """Test VIN decoder raises error on invalid VIN."""
    with pytest.raises(ValueError):
        VinDecoder.decode_vin("")  # Empty VIN
    with pytest.raises(ValueError):
        VinDecoder.decode_vin("SHORTVIN")  # Too short VIN

def test_vin_decoder_api_call(monkeypatch):
    """Test VIN decoder handles API calls."""
    dummy_data = {"Results": [{"Variable": "Make", "Value": "TestMake"}]}
    # Patch requests.get to return a dummy successful response
    monkeypatch.setattr(app.requests, 'get', lambda url: DummyResponse(200, dummy_data))
    result = VinDecoder.decode_vin("1HGCM82633A004352")
    assert result == dummy_data
    # Patch requests.get to simulate API error response
    monkeypatch.setattr(app.requests, 'get', lambda url: DummyResponse(500, {}))
    with pytest.raises(Exception):
        VinDecoder.decode_vin("1HGCM82633A004352")

def test_ai_reviewer_empty_code():
    """Test AIReviewer raises error on empty code input."""
    config = AppConfig()
    reviewer = AIReviewer(config)
    with pytest.raises(ValueError):
        reviewer.review_code("   ")

def test_ai_reviewer_review_code(monkeypatch):
    """Test AIReviewer with a mocked OpenAI response."""
    config = AppConfig()
    config.OPENAI_API_KEY = "test-key"
    reviewer = AIReviewer(config)

    # Create a dummy response object similar to OpenAI API response
    class DummyChoice:
        def __init__(self, content):
            # Emulate the message structure with content
            self.message = type("obj", (), {"content": content})

    class DummyResponse:
        def __init__(self, content):
            self.choices = [DummyChoice(content)]

    # Monkeypatch the OpenAI ChatCompletion.create method
    def dummy_create(model: str, messages: list) -> DummyResponse:
        return DummyResponse("Looks good, minimal issues.")

    monkeypatch.setattr(openai.ChatCompletion, 'create', dummy_create)

    review = reviewer.review_code("print('Hello, world!')")
    assert "Looks good" in review
