import pandas as pd
import numpy as np

def generate_congestion_dataset(num_samples=5000):
    np.random.seed(42)
    distances = np.random.uniform(0.1, 5.0, num_samples)
    road_classes = ['motorway', 'primary', 'secondary', 'tertiary', 'residential']
    sampled_roads = np.random.choice(road_classes, num_samples, p=[0.15, 0.25, 0.3, 0.2, 0.1])
    
    base_speeds = {'motorway': 80, 'primary': 50, 'secondary': 40, 'tertiary': 30, 'residential': 20}
    sampled_base_speeds = np.array([base_speeds[r] for r in sampled_roads])
    
    scenarios = ['Clear_Night', 'Dry_OffPeak', 'Morning_Rush', 'Evening_Rush', 'Monsoon_Rain']
    sampled_scenarios = np.random.choice(scenarios, num_samples, p=[0.15, 0.25, 0.25, 0.25, 0.1])
    
    scenario_multipliers = {'Clear_Night': 0.8, 'Dry_OffPeak': 1.0, 'Morning_Rush': 2.3, 'Evening_Rush': 2.6, 'Monsoon_Rain': 3.0}
    multipliers = np.array([scenario_multipliers[s] for s in sampled_scenarios])
    
    base_time_mins = (distances / sampled_base_speeds) * 60
    noise = np.random.normal(0, 0.4, num_samples)
    
    travel_cost = (base_time_mins * multipliers) + noise
    travel_cost = np.clip(travel_cost, 0.1, None)
    
    df = pd.DataFrame({
        'distance_km': distances,
        'road_class': sampled_roads,
        'base_speed_kph': sampled_base_speeds,
        'congestion_scenario': sampled_scenarios,
        'travel_cost': travel_cost
    })
    df.to_csv('ml/synthetic_congestion_data.csv', index=False)
    print(f"✅ Generated dataset at 'ml/synthetic_congestion_data.csv'")

if __name__ == "__main__":
    generate_congestion_dataset()