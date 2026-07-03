"""
predictor.py

Loads the trained XGBoost model and predicts
the routing cost of a road segment.
"""

from xgboost import XGBRegressor

from config import MODEL_FILE


class RouteCostPredictor:
    """
    Wrapper around the trained XGBoost model.
    """

    def __init__(self):

        self.model = XGBRegressor()

        self.model.load_model(MODEL_FILE)

    def predict(self, features):
        """
        Predict route cost.

        Parameters
        ----------
        features : dict

        Returns
        -------
        float
        """

        x = [[
            features["distance"],
            features["speed_limit"],
            features["traffic_factor"],
            features["road_penalty"],
            features["travel_time"]
        ]]

        prediction = self.model.predict(x)

        return float(prediction[0])