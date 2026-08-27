import pandas as pd
import numpy as np
from typing import Dict, Optional
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from scipy import stats


class AlphaModel:
    """Return-prediction model (ridge/lasso/random forest) scored by IC, not accuracy."""

    def __init__(self, model_type: str = 'ridge', **kwargs):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()

        if model_type == 'ridge':
            self.model = Ridge(**kwargs)
        elif model_type == 'lasso':
            self.model = Lasso(**kwargs)
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor(**kwargs)
        else:
            raise ValueError("model_type must be 'ridge', 'lasso', or 'random_forest'")

    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        # fit the scaler on train only - fitting on all data leaks test-set
        # mean/std back into training, a subtle but real lookahead
        self.scaler.fit(X_train)
        self.model.fit(self.scaler.transform(X_train), y_train)

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        return self.model.predict(self.scaler.transform(X_test))

    def evaluate(self, predictions: np.ndarray, y_actual: pd.Series) -> Dict:
        # IC (rank corr of prediction vs realised return) is the number that
        # matters - R^2 on noisy returns is hopeless, but ranking is enough to trade
        IC = stats.spearmanr(predictions, y_actual)[0]
        hit_rate = ((predictions > 0) == (y_actual > 0)).mean()
        return {'ic': IC, 'hit_rate': hit_rate, 'mean_pred': predictions.mean(), 'mean_actual': y_actual.mean()}

    def feature_importance(self, feature_names: list) -> pd.Series:
        if self.model_type in ['ridge', 'lasso']:
            importance = np.abs(self.model.coef_)
        elif self.model_type == 'random_forest':
            importance = self.model.feature_importances_
        else:
            raise ValueError("Feature importance not supported for this model type")
        return pd.Series(importance, index=feature_names).sort_values(ascending=False)
