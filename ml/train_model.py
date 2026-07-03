"""
train_model.py

Trains the XGBoost model used to estimate
road segment costs.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from xgboost import XGBRegressor

from config import MODEL_FILE


def train_model():
    """
    Train the XGBoost regression model.
    """

    print("Loading dataset...")

    dataset = pd.read_csv("data/routes.csv")

    feature_columns = [
        "distance",
        "speed_limit",
        "traffic_factor",
        "road_penalty",
        "travel_time",
    ]

    X = dataset[feature_columns]

    y = dataset["route_cost"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    print(f"Training samples : {len(X_train)}")
    print(f"Testing samples  : {len(X_test)}")

    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=200,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )

    print("\nTraining model...\n")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    print("=" * 50)
    print("Model Evaluation")
    print("=" * 50)

    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R²   : {r2:.4f}")

    print("\nFeature Importance")
    print("-" * 50)

    for feature, importance in sorted(
        zip(feature_columns, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True,
    ):
        print(f"{feature:<20} {importance:.4f}")

    model.save_model(MODEL_FILE)

    print("\nModel saved successfully.")
    print(MODEL_FILE)


if __name__ == "__main__":
    train_model()