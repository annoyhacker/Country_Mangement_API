import requests
from datetime import datetime
from ..models import Country, db
from tenacity import retry, stop_after_attempt, wait_random_exponential

@retry(stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=1, max=10))
def fetch_countries():
    """Fetch country data from RestCountries API"""
    try:
        response = requests.get(
            "https://restcountries.com/v3.1/all",
            headers={"User-Agent": "CountriesAPI/1.0"},
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Error: {str(e)}")
        return None

def transform_country_data(api_data):
    """Transform API data to database schema"""
    transformed = []
    for country in api_data:
        currencies = country.get('currencies', {})
        currency_code = list(currencies.keys())[0] if currencies else None
        currency_name = currencies.get(currency_code, {}).get('name') if currency_code else None
        
        transformed.append({
            "name": country.get('name', {}).get('common', ''),
            "cca3": country.get('cca3', ''),
            "currency_code": currency_code,
            "currency": currency_name,
            "capital": country.get('capital', [''])[0],
            "region": country.get('region', ''),
            "subregion": country.get('subregion', ''),
            "area": country.get('area', 0),
            "map_url": country.get('maps', {}).get('googleMaps', ''),
            "population": country.get('population', 0),
            "flag_url": country.get('flags', {}).get('png', '')
        })
    return transformed

def seed_countries():
    """Main seeding function"""
    api_data = fetch_countries()
    if not api_data:
        return False

    try:
        countries = transform_country_data(api_data)
        db.session.query(Country).delete()
        
        for country in countries:
            db.session.add(Country(**country))
            
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Database Error: {str(e)}")
        return False