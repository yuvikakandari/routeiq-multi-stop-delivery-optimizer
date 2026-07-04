# RouteIQ — Scenario-Based Multi-Stop Delivery Route Optimizer

A decision-support system that compares a distance-only delivery plan with a simulated-congestion, ML-weighted routing plan for the same multi-stop delivery batch.

## Table of Contents

* Project Overview
* Architecture Diagram
* Tech Stack
* How To Run
* Design Decisions
* Tradeoffs
* Evaluation Results
* Known Limitations
* Production Improvements

## 1. Project Overview

A decision-support system built to evaluate route optimization trade-offs among overall physical distance, predicted travel cost surfaces, and simulated ETAs under controlled congestion scenarios. A FastAPI backend snaps coordinate payloads to real-world OpenStreetMap driving graphs, applies an offline-trained XGBoost regressor model to calculate scenario-specific segment travel costs, and routes deliveries through a custom heap-based Dijkstra pathfinding engine. The system resolves combinatorial delivery sequences across a central depot and 3–6 user-selected drops using a nearest-neighbor sequencing heuristic, logging execution matrices directly to a local SQLite database for historical experiment tracking.

## 2. Architecture Diagram

```text
User Query (Streamlit Dashboard Control Panel)
      ↓
FastAPI Backend Gateway
      ↓                                    
Spatial Processing Layer
- Geopy address resolution / Snap interactive map clicks
- Map GPS coordinate inputs to closest OpenStreetMap graph nodes (OSMnx)
      ↓
Model Inference Pipeline
- Pass static topology vectors (length, road class, speed estimates) to XGBoost
- Apply controlled congestion scenario multipliers to compute segment costs
      ↓                                    
Optimization Core Engine
- Build all-pairs cost matrix across active batch destinations
- Execute Custom Heap-Based Dijkstra solver for least-cost paths
- Resolve deployment sequence via Nearest-Neighbor Tour Heuristic
      ↓                              
Persistence & Rendering Layer
- Write structural execution metrics to local SQLite ledger
- Render interactive trajectory tracks via Folium Map Layer
      ↓
Evaluation Dashboard Output
- Red Trajectory (Shortest-Distance Baseline) shown on map
- Blue Trajectory (RouteIQ Congestion-Aware Track) shown on map
- Tabular ledger of historical experiment deltas refreshed

```

End-to-end flow: Every request starts at the Streamlit frontend console where a dispatch manager selects an operational traffic scenario and sets 3–6 delivery pins either via interactive map clicks or text location queries. The frontend issues a REST API payload to the FastAPI backend microservice, which resolves spatial nodes from a cached local OpenStreetMap graph. The backend runs segment-by-segment cost inference through an XGBoost model, updates the active edge weights, and passes the graph to a custom heap-based Dijkstra engine. A nearest-neighbor sequence heuristic structures the optimal drop matrix, writes execution histories to an embedded SQLite table, and returns localized route vectors. The frontend renders both the distance baseline and optimized trajectories dynamically using Folium layers for interactive comparative analysis.

## 3. Tech Stack

| Component | Choice | Reason |
| --- | --- | --- |
| **Backend API Layer** | FastAPI 0.100+ | Asynchronous routing architecture, native Pydantic data validation, high throughput, and automated OpenAPI documentation generation. |
| **Server Gateway** | Uvicorn CLI | Lightweight ASGI server providing reliable local process loops and hot-reloading configurations during development. |
| **Machine Learning Model** | XGBoost 1.7+ | Gradient-boosted decision trees that deliver high-speed inference across multi-variable segment feature structures (road types, lengths, baseline speeds). |
| **Model Serialization** | Scikit-Learn | Robust model utility pipelines, label encoding, and training array configuration management tools. |
| **Spatial Graph Processing** | OSMnx 1.3+ / NetworkX | Automated downloading, filtering, and topological parsing of real-world OpenStreetMap road grids into directional multi-graphs. |
| **Geospatial Helpers** | Geopy / Shapely | Nominatim query processing for landmark address string resolution, geometric snapping, and coordinate proximity analysis. |
| **Dashboard Interface** | Streamlit 1.25+ | Zero-boilerplate frontend execution, interactive text and selector inputs, and native dashboard layout state management. |
| **Mapping Integration** | Folium / Streamlit-Folium | Flexible canvas rendering of geographic layouts, support for dynamic polyline arrays, and click-coordinate feedback capabilities. |
| **Vector Store / Ledger** | SQLite | Serverless, zero-configuration local persistence structure ideal for tracking individual execution history runs without system overhead. |
| **Unit Testing Suite** | Pytest | Automated assertion framework verifying Dijkstra algorithm math paths, disconnected node behavior, and sequencing arrays. |

## 4. How To Run

**Prerequisites:** Python 3.10+, Git, active terminal environment

### Step 1 — Clone and set up environment:

```powershell
git clone <your-repo-url>
cd routeiq-multi-stop-delivery-optimizer
python -m venv .venv

```

Activate the environment:

* **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
* **Mac/Linux:** `source .venv/bin/activate`

Install dependencies:

```powershell
pip install -r requirements.txt
pip install geopy

```

### Step 2 — Start the FastAPI Backend Daemon:

```powershell
uvicorn backend.main:app --reload

```

*(This initializes the core web server loop and runs the API engine locally on [http://127.0.0.1:8000](https://www.google.com/search?q=http://127.0.0.1:8000))*

### Step 3 — Launch the Dashboard Control Room:

Open a secondary independent terminal window, activate the `.venv` environment, and execute:

```powershell
streamlit run frontend/app.py

```

The terminal pipeline will automatically open an interactive web browser session targeting your local dashboard control panel at `http://localhost:8501`.

### Step 4 — Run Optimization Experiments:

1. Select a specific operational traffic template from the **Current Congestion Footprint** dropdown.
2. Enter a localized address inside the **Location Search Integration** bar (e.g., `"Connaught Place"`) or click directly on the interactive map canvas to drop 3 to 6 active pins.
3. Click the primary **Run Route Optimization Pipeline** button to trigger the execution matrices and save the metrics directly to the ledger.

## 5. Design Decisions

### 5.1 Custom Heap-Based Dijkstra Implementation

* **The decision:** Built a custom pathfinding solver using Python's native `heapq` module from scratch instead of relying on high-level black-box routing wrappers like NetworkX's built-in short path utilities.
* **Why own the pathfinding algorithm:** Using library wrappers makes it difficult to show deep algorithmic understanding to technical interview panels. Writing the min-heap traversal manually proves an ability to manipulate priority queues, optimize spatial node tracking, and handle low-level path reconstruction directly.
* **Algorithmic isolation:** The pathfinding logic is contained inside an independent module completely separate from FastAPI dependencies and model loading lines, making it easily testable via automated code scripts.

### 5.2 Decoupled Front-to-Backend Core Architecture

* **The decision:** Separated the project into an isolated presentation dashboard (`frontend/app.py`) and a completely separate REST API microservice backend (`backend/main.py`).
* **Why avoid a single script layout:** Putting spatial graph queries and model execution loops inside a single Streamlit file forces the dashboard thread to re-run heavy compute loops on every slider change or button click. Decoupling ensures that graph calculations are handled on a dedicated web server thread, keeping the user interface completely responsive.
* **Inter-process stability:** Communication between the interface and the optimization engine runs over standard JSON HTTP POST payloads, replicating how production logistics engines operate in real-world deployments.

### 5.3 Address Geocoding Resolution Bias

* **The decision:** Structured the input query processing system to automatically concatenate `, Delhi, India` to every raw text search string passed through Geopy's Nominatim interface.
* **Why hardcode regional string suffixes:** Open-source geocoders lack the massive semantic guessing power of paid proprietary mapping tools. A search query like `"Chanakyapuri"` can return random matches worldwide. Appending the regional suffix forces the spatial locator to bias its lookups within the target metropolitan boundary, resulting in clean, accurate coordinates for the project's road graph.

### 5.4 Database Choice and Schema Strategy

* **The decision:** Used an embedded, single-user SQLite instance to maintain local records rather than deploying an external database engine like PostgreSQL or MySQL.
* **Why choose SQLite over complex client-server platforms:** Since the system functions as a local experimental test bench for a single user, spinning up external database processes adds unnecessary deployment overhead without improving performance. SQLite provides reliable, zero-configuration local persistence that ensures the project remains lightweight and instantly executable upon cloning.
* **The structural normal form tradeoff:** The historical logging ledger stores execution results (stop count, baseline metrics, ML-derived ETAs, and net differences) in a single row transaction. This keeps database calls fast and lightweight while tracking key metrics across experiments without the need for complex relational tables.

## 6. Tradeoffs

### Native Python Heap Dijkstra vs. C-Optimized Solvers

Building the graph traversal script using native Python collections balances algorithmic readability and control against execution speed. C-compiled shortest-path extensions handle massive multi-million node matrices much faster. However, because the target OpenStreetMap graph boundaries are locked to a defined regional bounding box (under 50,000 nodes), processing latencies remain under 1 second, making a clean Python implementation perfect for project demonstrations.

### Address Text Searching vs. Full Autocomplete Interfaces

Utilizing an explicit text input box backed by a geocoding resolve button balances simple development and system reliability against character-by-character autocomplete menus. Integrating real-time dropdown autocomplete fields inside a Streamlit app requires building heavy JavaScript iframe messaging bridges (`window.parent.postMessage`) and introduces dependencies on external proprietary API keys. The text search field provides reliable spatial lookups without adding unstable frontend code.

### Offline Scenario Modeling vs. Continuous Live Data Feeds

Training the XGBoost model on engineered scenario codes balances predictable comparative analysis against live data streams. Consuming live traffic APIs makes testing unpredictable because street congestion fluctuates constantly throughout the day, making it hard to replicate a specific routing test case for an evaluation panel. Controlled scenarios let you demonstrate exactly how the engine alters its behavior across low, moderate, and high traffic settings using reproducible metrics.

## 7. Evaluation Results

### 7.1 Evaluation Dataset

A standardized evaluation matrix tracking identical multi-stop delivery routes (1 depot, 4 specific drop targets) across all 4 operational congestion scenarios to isolate optimization performance.

| # | Scenario | Stops | Distance Baseline ETA | ML-Weighted ETA | Calculated Efficiency Gain | Result |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `Clear_Night` | 4 Stops | 12.57 mins | 11.25 mins | -10.5% Predicted Time | ✓ PASS |
| 2 | `Morning_Rush` | 4 Stops | 53.44 mins | 49.16 mins | -8.0% Predicted Time | ✓ PASS |
| 3 | `Monsoon_Rain` | 4 Stops | 53.49 mins | 48.36 mins | -9.6% Predicted Time | ✓ PASS |
| 4 | `Evening_Rush` | 4 Stops | 55.60 mins | 51.09 mins | -8.1% Predicted Time | ✓ PASS |

### 7.2 Summary

| Metric | Result |
| --- | --- |
| **Routing Behavior Consistency** | 4/4 test cases successfully executed both the baseline distance route and the ML-weighted optimization route without graph disconnection errors. |
| **Algorithmic Path Divergence** | The pathfinding core correctly identified structural detours in all high-congestion scenarios (`Morning_Rush`, `Evening_Rush`, `Monsoon_Rain`), routing travel vectors away from choked central corridors. |
| **Tour Sequence Logic** | The nearest-neighbor sequencing engine generated clean delivery patterns across all test runs, positioning spatially constrained nodes effectively to close the routing loops. |
| **Persistence Automation** | 100% of the optimization runs were captured by the SQLite backend engine and displayed inside the frontend history log. |

### 7.3 Performance

| Scenario | Latency |
| --- | --- |
| **API Optimization Loop (End-to-End)** | 0.40 - 0.75 seconds |
| **Database History Pull** | 0.02 - 0.05 seconds |
| **Geocoding Landmark Search** | 1.10 - 2.30 seconds *(Dependent on Nominatim remote API response times)* |
| **Initial Backend Boot & Graph Load** | 4.00 - 7.00 seconds |

Processing speed is dominated by the initial loading of the regional OpenStreetMap network file. Once the spatial graph structures are parsed into memory, the optimization computations (including XGBoost inference, Dijkstra path calculations, and sequencing logic) execute locally in under 1 second.

## 8. Known Limitations

* **Macro Spatial Bounding Box:** To optimize memory consumption and ensure fast user interface refreshes, the active OpenStreetMap network is restricted to a cached regional urban grid. Attempting to compute nationwide delivery plans would exhaust system RAM resources without building dedicated sub-network partitioning structures.
* **Intersection Turning Penalties:** The custom pathfinding engine views street junctions as mathematical vertices and strictly respects one-way vector tracks. However, it does not factor in structural intersection delays, turn restrictions (e.g., prohibited right turns), or traffic light signal cycles.
* **Synthetic Congestion Data:** The underlying XGBoost regressor calculates segment weights using engineered scenario codes rather than real-world GPS probe logs or live traffic data feeds. As a result, route metrics represent controlled comparative experiments rather than real-world production navigation.

## 9. Production Improvements

* **Contraction Hierarchies Preprocessing:** Integrate a graph preprocessing layer to establish core shortcut highways across the network layout. This accelerates Dijkstra query times when scaling the system to handle larger multi-city regions.
* **Relational Database Migration:** Migrate the database layer from a local SQLite setup to a dedicated PostgreSQL server backed by the PostGIS spatial extension. This allows the system to support concurrent multi-user tracking and perform complex polygon intersection queries.
* **Asynchronous Task Queuing:** Deploy Celery alongside a Redis message broker to run optimization calculations on separate worker nodes. This prevents long-running graph calculations from blocking backend threads, helping the system scale to handle multiple concurrent requests.
* **Turn-Restricted Path Expansion:** Upgrade the core pathfinding script from a node-based routing engine to an edge-based routing engine. This allows the system to incorporate turning constraints and real-world junction delays into its cost matrices.