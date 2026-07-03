"""
dijkstra.py

Manual implementation of Dijkstra's Algorithm.

This implementation:
- Uses a priority queue (heapq)
- Computes shortest paths based on a specified edge weight
- Reconstructs the optimal route
- Does NOT use networkx.shortest_path()
"""

import heapq


def reconstruct_path(previous_nodes, start_node, end_node):
    """
    Reconstruct shortest path from start to end.

    Parameters
    ----------
    previous_nodes : dict
        Stores parent of each node.
    start_node : int
    end_node : int

    Returns
    -------
    list
        Ordered list of nodes in the shortest path.
    """

    path = []

    current = end_node

    while current is not None:
        path.append(current)
        current = previous_nodes[current]

    path.reverse()

    if path[0] == start_node:
        return path

    return []


def dijkstra(graph, start_node, end_node, weight="length"):
    """
    Compute shortest path using Dijkstra's Algorithm.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
    start_node : int
    end_node : int
    weight : str
        Edge attribute to optimize.
        Examples:
        - length
        - predicted_cost (future)

    Returns
    -------
    tuple
        (total_cost, path)
    """

    distances = {
        node: float("inf")
        for node in graph.nodes
    }

    previous_nodes = {
        node: None
        for node in graph.nodes
    }

    distances[start_node] = 0

    priority_queue = [
        (0, start_node)
    ]

    while priority_queue:

        current_distance, current_node = heapq.heappop(
            priority_queue
        )

        if current_node == end_node:
            break

        if current_distance > distances[current_node]:
            continue

        for neighbor in graph.neighbors(current_node):

            edge_data = graph.get_edge_data(
                current_node,
                neighbor
            )

            if not edge_data:
                continue

            minimum_weight = float("inf")

            for edge in edge_data.values():
                edge_weight = edge.get(weight, float("inf"))
                if edge_weight < minimum_weight:
                    minimum_weight = edge_weight
            edge_weight = minimum_weight
            new_distance = (
                current_distance +
                edge_weight
            )

            if new_distance < distances[neighbor]:

                distances[neighbor] = new_distance

                previous_nodes[neighbor] = current_node

                heapq.heappush(
                    priority_queue,
                    (
                        new_distance,
                        neighbor
                    )
                )

    path = reconstruct_path(
        previous_nodes,
        start_node,
        end_node
    )

    return (
        distances[end_node],
        path
    )