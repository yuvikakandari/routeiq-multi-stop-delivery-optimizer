"""
intelligent_router.py

Integrates machine learning with graph routing.
"""

from algorithms.graph_loader import get_graph
from algorithms.dijkstra import dijkstra

from ml.feature_engineering import extract_edge_features
from ml.predictor import RouteCostPredictor


class IntelligentRouter:

    def __init__(self):

        self.graph = get_graph()

        self.predictor = RouteCostPredictor()

    def assign_predicted_costs(self):
        """
        Predict cost for every edge in the graph.
        """

        print("Predicting edge costs...")

        for _, _, _, edge in self.graph.edges(keys=True, data=True):

            features = extract_edge_features(edge)

            predicted_cost = self.predictor.predict(features)

            edge["predicted_cost"] = predicted_cost

    def shortest_route(
        self,
        start_node,
        end_node
    ):
        """
        Compute shortest route using predicted costs.
        """

        return dijkstra(
            self.graph,
            start_node,
            end_node,
            weight="predicted_cost"
        )
 
    def route_coordinates(self, path):
        """
        Convert graph node IDs into latitude/longitude coordinates.

        Parameters
        ----------
        path : list[int]

        Returns
        -------
        list[dict]
        """

        coordinates = []

        for node in path:
            coordinates.append({
                "lat": self.graph.nodes[node]["y"],
                "lon": self.graph.nodes[node]["x"]
            })

        return coordinates

