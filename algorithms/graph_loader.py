"""
graph_loader.py

Downloads and loads the OpenStreetMap road network
for the configured city.

The graph is cached locally as a GraphML file to avoid
downloading it every time the application starts.
"""

from pathlib import Path

import osmnx as ox
import networkx as nx

from config import (
    CITY_NAME,
    NETWORK_TYPE,
    GRAPH_FILE,
)


def download_graph():
    """
    Download the road network graph for the configured city.

    Returns
    -------
    networkx.MultiDiGraph
        Road network graph.
    """

    print(f"Downloading road network for {CITY_NAME}...")

    graph = ox.graph_from_place(
        CITY_NAME,
        network_type=NETWORK_TYPE,
    )

    return graph


def save_graph(graph: nx.MultiDiGraph):
    """
    Save the graph locally.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        Road network graph.
    """

    ox.save_graphml(graph, GRAPH_FILE)


def load_cached_graph():
    """
    Load a previously saved graph.

    Returns
    -------
    networkx.MultiDiGraph
    """

    return ox.load_graphml(GRAPH_FILE)


def get_graph():
    """
    Return the city graph.

    If a cached version exists, load it.
    Otherwise download it and save it.

    Returns
    -------
    networkx.MultiDiGraph
    """

    if Path(GRAPH_FILE).exists():

        print("Loading cached graph...")

        return load_cached_graph()

    graph = download_graph()

    save_graph(graph)

    return graph