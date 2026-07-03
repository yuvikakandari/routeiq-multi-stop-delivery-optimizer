"""
feature_engineering.py

Extracts numerical features from an OpenStreetMap road edge.
"""

import random

from config import RANDOM_SEED

random.seed(RANDOM_SEED)

# Estimated urban speed limits (km/h)
ROAD_SPEEDS = {
    "motorway": 90,
    "trunk": 80,
    "primary": 60,
    "secondary": 50,
    "tertiary": 40,
    "residential": 30,
    "service": 20,
}

# Road penalty used during target generation
ROAD_PENALTY = {
    "motorway": 0.2,
    "trunk": 0.3,
    "primary": 0.5,
    "secondary": 0.7,
    "tertiary": 0.9,
    "residential": 1.2,
    "service": 1.5,
}


def normalize_highway(highway):
    """
    OSM sometimes stores highway as a list.
    """

    if isinstance(highway, list):
        return highway[0]

    return highway


def estimate_speed(highway):
    """
    Estimate speed limit.
    """

    highway = normalize_highway(highway)

    return ROAD_SPEEDS.get(highway, 30)


def estimate_road_penalty(highway):
    """
    Penalty associated with road type.
    """

    highway = normalize_highway(highway)

    return ROAD_PENALTY.get(highway, 1.0)


def simulate_traffic(highway):
    """
    Simulate congestion.

    Better roads generally have lower congestion.
    """

    highway = normalize_highway(highway)

    ranges = {
        "motorway": (1.0, 1.15),
        "trunk": (1.0, 1.20),
        "primary": (1.05, 1.30),
        "secondary": (1.10, 1.45),
        "tertiary": (1.15, 1.60),
        "residential": (1.20, 1.80),
        "service": (1.20, 2.00),
    }

    low, high = ranges.get(highway, (1.1, 1.8))

    return random.uniform(low, high)


def extract_edge_features(edge):
    """
    Extract ML features from one road edge.
    """

    distance = edge.get("length", 0)

    highway = normalize_highway(
        edge.get("highway", "residential")
    )

    speed = estimate_speed(highway)

    traffic = simulate_traffic(highway)

    speed_mps = speed * 1000 / 3600

    travel_time = distance / speed_mps

    road_penalty = estimate_road_penalty(highway)

    return {
        "distance": distance,
        "speed_limit": speed,
        "traffic_factor": traffic,
        "travel_time": travel_time,
        "road_penalty": road_penalty,
    }