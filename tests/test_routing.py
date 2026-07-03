# tests/test_routing.py
import pytest
import networkx as nx
from backend.router import custom_dijkstra, nearest_neighbor_tsp

@pytest.fixture
def sample_graph():
    """Builds a predictable multi-edge graph for routing tests."""
    G = nx.MultiGraph()
    # Path 1: Direct but expensive edge
    G.add_edge(1, 3, key=0, length=50.0)
    # Path 2: Two cheaper hops (1 -> 2 -> 3) total length = 25.0
    G.add_edge(1, 2, key=0, length=10.0)
    G.add_edge(2, 3, key=0, length=15.0)
    return G

def test_dijkstra_shortest_path(sample_graph):
    """Verifies that the custom heap-Dijkstra accurately finds the lowest cost path."""
    cost, path = custom_dijkstra(sample_graph, start_node=1, target_node=3, weight_attribute="length")
    assert cost == 25.0
    assert path == [1, 2, 3]

def test_dijkstra_unreachable_nodes():
    """Ensures that isolated nodes return infinite cost and an empty path array."""
    G = nx.MultiGraph()
    G.add_node(1)
    G.add_node(2) # Completely disconnected
    
    cost, path = custom_dijkstra(G, start_node=1, target_node=2, weight_attribute="length")
    assert cost == float('inf')
    assert path == []

def test_nearest_neighbor_sequencing():
    """Validates the stop-ordering TSP heuristic pathing choices."""
    nodes = [0, 1, 2] # 0 is Depot, 1 and 2 are delivery locations
    # Symmetric cost matrix
    cost_matrix = {
        (0, 1): 5,  (1, 0): 5,
        (0, 2): 15, (2, 0): 15,
        (1, 2): 4,  (2, 1): 4
    }
    # From 0, node 1 is closer (cost 5) than node 2 (cost 15). 
    # From 1, it must visit 2 (cost 4), then return to 0 (cost 15). Total = 24.
    tour, total_cost = nearest_neighbor_tsp(nodes, cost_matrix)
    assert tour == [0, 1, 2, 0]
    assert total_cost == 24.0