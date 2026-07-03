# RouteIQ — Scenario-Based Multi-Stop Delivery Route Optimizer

RouteIQ is an optimization engine and decision-support system designed to evaluate whether a simulated congestion-aware, machine-learning-weighted routing plan produces lower travel costs than a standard distance-only routing baseline for the same delivery batch. 

Running on real-world OpenStreetMap topological data, the platform combines a custom heap-based pathfinding engine, a machine learning segment-cost model, a stop-sequencing heuristic, and an embedded persistence layer to analyze logistics efficiency across varying urban traffic profiles.

---

## 🏗️ System Architecture

```text
  [ Interactive Folium Map Panel ] <--- (User Click / Geopy String Geocoder)
                |
                v (REST API POST)
     [ FastAPI Endpoint Service ] 
                |
                +---> 1. Map GPS Inputs to Local OSM Network Nodes (OSMnx/NetworkX)
                |
                +---> 2. Dynamic Weighting: Runs Segment Inference via XGBoost Model
                |
                +---> 3. Optimization: Resolves Custom Heap-Dijkstra & Sequence Heuristic
                |
                v (SQL Transaction)
   [ Embedded SQLite Log Database ] ---> (Renders Historical Evaluation Table)