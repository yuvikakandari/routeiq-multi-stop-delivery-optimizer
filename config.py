"""
config.py

Central configuration for the Route Optimization Platform.
"""

from pathlib import Path

# --------------------------------------------------------
# Project Directories
# --------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# --------------------------------------------------------
# OpenStreetMap
# --------------------------------------------------------

CITY_NAME = "New Delhi, India"
NETWORK_TYPE = "drive"

GRAPH_FILE = DATA_DIR / "city_graph.graphml"

# --------------------------------------------------------
# Machine Learning
# --------------------------------------------------------

MODEL_FILE = MODELS_DIR / "xgboost_route_model.json"

# --------------------------------------------------------
# Randomness
# --------------------------------------------------------

RANDOM_SEED = 42