# processing/utils/geo.py

# Country name / demonym → ISO 3166-1 alpha-2 mapping
# Extend this list as your corpus grows

LOCATION_TO_COUNTRY = {
    # Countries
    "india": "IN", "pakistan": "PK", "china": "CN", "united states": "US",
    "usa": "US", "america": "US", "uk": "GB", "united kingdom": "GB",
    "britain": "GB", "england": "GB", "russia": "RU", "germany": "DE",
    "france": "FR", "japan": "JP", "australia": "AU", "canada": "CA",
    "brazil": "BR", "israel": "IL", "ukraine": "UA", "iran": "IR",
    "saudi arabia": "SA", "south korea": "KR", "taiwan": "TW",
    # Indian cities / states → IN
    "mumbai": "IN", "delhi": "IN", "new delhi": "IN", "bangalore": "IN",
    "bengaluru": "IN", "chennai": "IN", "hyderabad": "IN", "kolkata": "IN",
    "pune": "IN", "ahmedabad": "IN", "gujarat": "IN", "maharashtra": "IN",
    "tamil nadu": "IN", "karnataka": "IN", "rajasthan": "IN",
    # US cities → US
    "new york": "US", "washington": "US", "los angeles": "US",
    "san francisco": "US", "chicago": "US", "seattle": "US",
    # Other major cities
    "london": "GB", "paris": "FR", "berlin": "DE", "beijing": "CN",
    "shanghai": "CN", "tokyo": "JP", "moscow": "RU", "sydney": "AU",
}


def infer_country(locations: list[str], source_region: str) -> str | None:
    """
    Try to infer a primary country from extracted location entities.
    Falls back to source_region if no match found.
    """
    for loc in locations:
        code = LOCATION_TO_COUNTRY.get(loc.lower().strip())
        if code:
            return code
    # fallback to source region if it looks like a country code
    if source_region and len(source_region) == 2:
        return source_region.upper()
    return None