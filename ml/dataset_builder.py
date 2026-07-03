"""
dataset_builder.py

Creates the ML training dataset from
the OpenStreetMap road graph.
"""

import pandas as pd

from algorithms.graph_loader import get_graph
from ml.feature_engineering import extract_edge_features


def compute_route_cost(features):
    """
    Synthetic target used for ML.

    The model learns this value.
    """

    return (
        0.50 * features["travel_time"]
        + 0.30 * features["traffic_factor"]
        + 0.20 * features["road_penalty"]
    )


def build_dataset():

    graph = get_graph()

    rows = []

    print("Generating training dataset...")

    for _, _, edge in graph.edges(data=True):

        features = extract_edge_features(edge)

        cost = compute_route_cost(features)

        rows.append({

            "distance": features["distance"],

            "speed_limit": features["speed_limit"],

            "traffic_factor": features["traffic_factor"],

            "road_penalty": features["road_penalty"],

            "travel_time": features["travel_time"],

            "route_cost": cost

        })

    dataset = pd.DataFrame(rows)

    dataset.to_csv(
        "data/routes.csv",
        index=False
    )

    print(dataset.head())

    print(f"\nDataset size: {len(dataset)}")

    return dataset


if __name__ == "__main__":
    build_dataset()