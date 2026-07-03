import osmnx as ox
import heapq
import numpy as np
import joblib
import json
import pandas as pd
from shapely.geometry import LineString

# Change lines 8-12 at the top of backend/router.py to this:
G_raw = ox.load_graphml("backend/delhi_road_network.graphml")
# Convert the directed MultiDiGraph to an undirected MultiGraph natively
import networkx as nx
G = nx.MultiGraph(G_raw)
# Delhi Central Warehouse Depot Location (Anchored near Connaught Place)
WAREHOUSE_LOCATION = (28.6139, 77.2090) 
WAREHOUSE_NODE = ox.distance.nearest_nodes(G, WAREHOUSE_LOCATION[1], WAREHOUSE_LOCATION[0])

try:
    xgb_model = joblib.load('ml/travel_cost_xgb.pkl')
    with open('ml/model_features.json', 'r') as f:
        model_features = json.load(f)
except FileNotFoundError:
    xgb_model, model_features = None, None

def apply_ml_weights(graph, scenario):
    if xgb_model is None or model_features is None:
        return
    edge_data_list, edge_keys = [], []
    for u, v, k, data in graph.edges(keys=True, data=True):
        highway = data.get("highway", "residential")
        road_class = highway[0] if isinstance(highway, list) else highway
        speed_map = {'motorway': 80, 'primary': 50, 'secondary': 40, 'tertiary': 30, 'residential': 20}
        edge_data_list.append({
            'distance_km': float(data.get("length", 100)) / 1000.0,
            'road_class': road_class,
            'base_speed_kph': speed_map.get(road_class, 20),
            'congestion_scenario': scenario
        })
        edge_keys.append((u, v, k))

    df_encoded = pd.get_dummies(pd.DataFrame(edge_data_list), drop_first=False).reindex(columns=model_features, fill_value=0)
    predicted_costs = xgb_model.predict(df_encoded)
    for idx, (u, v, k) in enumerate(edge_keys):
        graph[u][v][k]['predicted_cost'] = float(predicted_costs[idx])

def custom_dijkstra(graph, start_node, target_node, weight_attribute="length"):
    pq = [(0.0, start_node)]
    costs = {start_node: 0.0}
    predecessors = {start_node: None}
    
    while pq:
        current_cost, u = heapq.heappop(pq)
        if u == target_node:
            break
        if current_cost > costs.get(u, float('inf')):
            continue
        for v in graph.neighbors(u):
            edge_data = graph.get_edge_data(u, v)
            edge_attribs = list(edge_data.values())[0] if isinstance(edge_data, dict) else edge_data
            weight = float(edge_attribs.get(weight_attribute, edge_attribs.get("length", 1.0)))
            new_cost = current_cost + weight
            if new_cost < costs.get(v, float('inf')):
                costs[v] = new_cost
                predecessors[v] = u
                heapq.heappush(pq, (new_cost, v))
                
    if target_node not in costs:
        return float('inf'), []
    path = []
    curr = target_node
    while curr is not None:
        path.append(curr)
        curr = predecessors[curr]
    path.reverse()
    return costs[target_node], path

def nearest_neighbor_tsp(all_nodes, cost_matrix):
    n = len(all_nodes)
    unvisited = set(range(1, n))
    current_idx, tour, total_cost = 0, [0], 0.0
    while unvisited:
        next_idx = min(unvisited, key=lambda x: cost_matrix.get((current_idx, x), float('inf')))
        total_cost += cost_matrix.get((current_idx, next_idx), float('inf'))
        tour.append(next_idx)
        unvisited.remove(next_idx)
        current_idx = next_idx
    total_cost += cost_matrix.get((current_idx, 0), float('inf'))
    tour.append(0)
    return tour, total_cost

def evaluate_routing_plans(delivery_locations, scenario="Morning_Rush"):
    apply_ml_weights(G, scenario)
    delivery_nodes = [ox.distance.nearest_nodes(G, lon, lat) for lat, lon in delivery_locations]
    all_batch_nodes = [WAREHOUSE_NODE] + delivery_nodes
    n = len(all_batch_nodes)

    distance_matrix, ml_cost_matrix, dist_paths, ml_paths = {}, {}, {}, {}
    for i in range(n):
        for j in range(n):
            if i != j:
                d_cost, d_path = custom_dijkstra(G, all_batch_nodes[i], all_batch_nodes[j], "length")
                distance_matrix[(i, j)], dist_paths[(i, j)] = d_cost, d_path
                m_cost, m_path = custom_dijkstra(G, all_batch_nodes[i], all_batch_nodes[j], "predicted_cost")
                ml_cost_matrix[(i, j)], ml_paths[(i, j)] = m_cost, m_path

    seq_dist, _ = nearest_neighbor_tsp(all_batch_nodes, distance_matrix)
    seq_ml, _ = nearest_neighbor_tsp(all_batch_nodes, ml_cost_matrix)

    def extract_route_metrics(sequence, paths_cache):
        full_route_latlon = []
        total_distance_km = 0.0
        total_simulated_eta_min = 0.0
        for idx in range(len(sequence) - 1):
            i, j = sequence[idx], sequence[idx + 1]
            node_path = paths_cache.get((i, j), [])
            for u, v in zip(node_path[:-1], node_path[1:]):
                edge_data = G.get_edge_data(u, v)
                edge_attribs = list(edge_data.values())[0] if isinstance(edge_data, dict) else edge_data
                length_m = float(edge_attribs.get("length", 0.0))
                total_distance_km += length_m / 1000.0
                total_simulated_eta_min += float(edge_attribs.get("predicted_cost", length_m / 1000.0))
                if "geometry" in edge_attribs:
                    line: LineString = edge_attribs["geometry"]
                    full_route_latlon.extend(list(zip(line.xy[1], line.xy[0])))
                else:
                    full_route_latlon.append((G.nodes[u]['y'], G.nodes[u]['x']))
        return full_route_latlon, round(total_distance_km, 2), round(total_simulated_eta_min, 2)

    geo_dist, d_km, d_eta = extract_route_metrics(seq_dist, dist_paths)
    geo_ml, m_km, m_eta = extract_route_metrics(seq_ml, ml_paths)

    return {
        "baseline": {"path": geo_dist, "distance": d_km, "eta": d_eta, "sequence": [int(x) for x in seq_dist]},
        "optimized": {"path": geo_ml, "distance": m_km, "eta": m_eta, "sequence": [int(x) for x in seq_ml]}
    }