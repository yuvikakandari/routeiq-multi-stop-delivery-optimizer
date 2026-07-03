import osmnx as ox
import os

def download_regional_graph():
    # Ensure the script correctly references the backend directory structure
    backend_dir = "backend"
    os.makedirs(backend_dir, exist_ok=True)

    print("🌐 Fetching real-world road network topology from OpenStreetMap for Delhi NCR...")
    
    # Delhi Central Coordinates (Anchored near Connaught Place / Central Hub)
    delhi_lat, delhi_lon = 28.6139, 77.2090

    # Download the drivable public road network within a 6km radius of the depot 
    # to cleanly encapsulate major surrounding transit arteries (Ring Road, Connaught lanes, etc.)
    G = ox.graph_from_point((delhi_lat, delhi_lon), dist=6000, network_type="drive")

    output_path = os.path.join(backend_dir, "delhi_road_network.graphml")
    
    # Serialize and save the network graph locally
    ox.save_graphml(G, filepath=output_path)
    print(f"✅ Map topology successfully downloaded and saved to: {output_path}")

if __name__ == "__main__":
    download_regional_graph()