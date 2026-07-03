"""
generate_dataset.py

Generates a machine learning dataset from the OpenStreetMap
road network.

Each road segment becomes one training sample.
"""

import pandas as pd

from algorithms.graph_loader import get_graph
from ml.feature_engineering import edge_features


def generate_dataset():
    """
    Generate a dataset from all edges in the road network.

    Returns
    -------
    pandas.DataFrame
    """

    graph = get_graph()

    rows = []

    print("Generating dataset...")

    for u, v, edge in graph.edges(data=True):

        features = edge_features(edge)

        # ------------------------------
        # Target value
        # ------------------------------
        # For now we use travel_time as the
        # regression target.
        #
        # Later we'll replace this with
        # smarter route cost estimation.
        # ------------------------------

        rows.append({
            "distance": features["distance"],
            "speed_limit": features["speed_limit"],
            "traffic_factor": features["traffic_factor"],
            "travel_time": features["travel_time"]
        })

    dataset = pd.DataFrame(rows)

    dataset.to_csv(
        "data/routes.csv",
        index=False
    )

    print(f"Dataset saved with {len(dataset)} rows.")

    return dataset


if __name__ == "__main__":
    generate_dataset()