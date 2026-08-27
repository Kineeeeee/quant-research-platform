import pandas as pd
import numpy as np
from typing import Dict
from sklearn.model_selection import TimeSeriesSplit
from src.ml.features import FeatureBuilder
from src.ml.model import AlphaModel


class MLPipeline:
    """
    End-to-end: prices -> features -> time-series CV -> predict -> score by IC.
    The real question is whether ML beats plain momentum/value, so the bar is
    a positive, stable IC across folds - not in-sample R^2.
    """

    def __init__(
        self,
        prices: pd.Series,
        model_type: str = 'ridge',
        forward_period: int = 21,
        n_splits: int = 5,
    ):
        self.prices = prices
        self.model_type = model_type
        self.forward_period = forward_period
        self.n_splits = n_splits

    def run(self) -> Dict:
        fb = FeatureBuilder(self.prices)
        X, y = fb.build(self.forward_period)
        # TimeSeriesSplit, never a random split - training must always be on the
        # past, testing on the future, or the IC is a fantasy
        tscv = TimeSeriesSplit(n_splits=self.n_splits)

        results = []
        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            model = AlphaModel(model_type=self.model_type)
            model.train(X_train, y_train)
            predictions = model.predict(X_test)
            results.append(model.evaluate(predictions, y_test))

        avg_ic = np.mean([r['ic'] for r in results])
        return {'predictions': predictions, 'actuals': y_test,
                'metrics_per_fold': results, 'avg_ic': avg_ic}

    def print_summary(self, result: Dict):
        print("=== ML PIPELINE SUMMARY ===")
        for i, fold in enumerate(result['metrics_per_fold']):
            print(f"Fold {i+1}: IC={fold['ic']:.4f}, Hit Rate={fold['hit_rate']:.4f}")
        print(f"Average IC: {result['avg_ic']:.4f}")
        if result['avg_ic'] > 0.03:
            print("Conclusion: ML adds alpha")
        elif result['avg_ic'] < 0.01:
            print("Conclusion: ML does not add alpha")
