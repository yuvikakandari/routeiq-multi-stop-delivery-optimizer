from algorithms.graph_loader import get_graph
from routing.location_mapper import get_nearest_node
from routing.intelligent_router import IntelligentRouter

graph = get_graph()

router = IntelligentRouter()

router.assign_predicted_costs()

# Example coordinates
# India Gate
start_lat = 28.6129
start_lon = 77.2295

# Connaught Place
end_lat = 28.6315
end_lon = 77.2167

start_node = get_nearest_node(
    graph,
    start_lat,
    start_lon
)

end_node = get_nearest_node(
    graph,
    end_lat,
    end_lon
)

cost, path = router.shortest_route(
    start_node,
    end_node
)

print("=" * 50)
print("Route Optimization Result")
print("=" * 50)
print(f"Predicted Cost : {cost:.2f}")
print(f"Nodes in Path  : {len(path)}")