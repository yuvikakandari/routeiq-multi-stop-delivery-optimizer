"""
geocoding.py

Converts human-readable location names into latitude/longitude
coordinates using OpenStreetMap's Nominatim geocoder.
"""

import osmnx as ox


def geocode_location(location_name):
    """
    Convert a place name or address into latitude and longitude.

    Parameters
    ----------
    location_name : str
        Example: "India Gate, New Delhi"

    Returns
    -------
    tuple[float, float]
        Latitude and longitude.

    Raises
    ------
    ValueError
        If the location cannot be found.
    """

    try:
        latitude, longitude = ox.geocode(location_name)
        return latitude, longitude

    except Exception as error:
        raise ValueError(
            f"Could not find location: {location_name}"
        ) from error