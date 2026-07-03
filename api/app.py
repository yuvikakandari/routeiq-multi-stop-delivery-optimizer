"""
app.py

FastAPI backend for the Route Optimization Platform.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from algorithms.graph_loader import get_graph
from routing.geocoding import geocode_location
from routing.intelligent_router import IntelligentRouter
from routing.location_mapper import get_nearest_node


app = FastAPI(
    title="Route Optimization API",
    version="1.0.0",
)

graph = get_graph()
router = IntelligentRouter()
router.assign_predicted_costs()


class RouteRequest(BaseModel):
    """Request body for coordinate-based routing."""

    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float


class LocationRouteRequest(BaseModel):
    """Request body for place-name-based routing."""

    start_location: str
    end_location: str


def build_route_response(start_lat, start_lon, end_lat, end_lon):
    """
    Map coordinates to graph nodes, compute an optimized route,
    and return frontend-ready route data.
    """

    start_node = get_nearest_node(
        graph,
        start_lat,
        start_lon,
    )

    end_node = get_nearest_node(
        graph,
        end_lat,
        end_lon,
    )

    cost, path = router.shortest_route(
        start_node,
        end_node,
    )

    if not path:
        raise HTTPException(
            status_code=404,
            detail="No drivable route was found between these locations.",
        )

    coordinates = router.route_coordinates(path)

    return {
        "predicted_cost": cost,
        "path_length": len(path),
        "coordinates": coordinates,
        "start": {
            "lat": start_lat,
            "lon": start_lon,
        },
        "destination": {
            "lat": end_lat,
            "lon": end_lon,
        },
    }


@app.get("/")
def health():
    """Basic API health-check endpoint."""

    return {"status": "running"}


@app.post("/route")
def optimize_route(request: RouteRequest):
    """Compute an optimized route from latitude/longitude coordinates."""

    return build_route_response(
        request.start_lat,
        request.start_lon,
        request.end_lat,
        request.end_lon,
    )


@app.post("/route-by-name")
def optimize_route_by_name(request: LocationRouteRequest):
    """Geocode two place names and compute an optimized route."""

    try:
        start_lat, start_lon = geocode_location(
            request.start_location
        )

        end_lat, end_lon = geocode_location(
            request.end_location
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return build_route_response(
        start_lat,
        start_lon,
        end_lat,
        end_lon,
    )