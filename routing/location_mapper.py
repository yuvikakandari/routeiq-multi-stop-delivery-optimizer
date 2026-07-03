"""
location_mapper.py

Converts latitude/longitude coordinates into the
nearest node in the OpenStreetMap graph.
"""

import osmnx as ox


def get_nearest_node(graph, latitude, longitude):
    """
    Find the nearest graph node to a GPS coordinate.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
    latitude : float
    longitude : float

    Returns
    -------
    int
        Node ID
    """

    node = ox.distance.nearest_nodes(
        graph,
        X=longitude,
        Y=latitude
    )

    return node