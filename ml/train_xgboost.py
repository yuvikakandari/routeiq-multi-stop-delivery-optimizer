import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import root_mean_squared_error, r2_score
import joblib
import json

def train_edge_cost_model():
    df = pd.read_csv('ml/synthetic_congestion_data.csv')
    X = pd.get_dummies(df[['distance_km', 'road_class', 'base_speed_kph', 'congestion_scenario']], drop_first=False)
    y = df['travel_cost']
    
    feature_columns = list(X.columns)
    with open('ml/model_features.json', 'w') as f:
        json.dump(feature_columns, f)
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = xgb.XGBRegressor(n_estimators=150, max_depth=5, learning_rate=0.08, subsample=0.8, random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    print(f"📊 RMSE: {root_mean_squared_error(y_test, predictions):.4f} | R²: {r2_score(y_test, predictions):.4f}")
    
    joblib.dump(model, 'ml/travel_cost_xgb.pkl')
    print("✅ Model saved at 'ml/travel_cost_xgb.pkl'")

if __name__ == "__main__":
    train_edge_cost_model()