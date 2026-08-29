import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


EXPERIMENTS_FILE = 'experiments.json'


class ExperimentTracker:
    """
    Append-only log of every run (params + metrics + timestamp) to a JSON file,
    so later you can ask "what was my best momentum config?" instead of
    scrolling terminal history. Deliberately dumb - a file, not a database.
    """

    def __init__(self, filepath: str = EXPERIMENTS_FILE):
        self.filepath = filepath
        self.experiments: List[Dict] = []
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.experiments = json.load(f)
            except json.JSONDecodeError:
                # corrupt/half-written file - start clean rather than crash
                self.experiments = []
        else:
            self.experiments = []

    def _save(self):
        dirname = os.path.dirname(self.filepath)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(self.filepath, 'w') as f:
            json.dump(self.experiments, f, indent=2)

    def log(self, name: str, params: Dict, metrics: Dict, data_period: str = "", notes: str = "") -> int:
        record = {
            'id': max([e['id'] for e in self.experiments], default=-1) + 1,
            'timestamp': datetime.now().isoformat(),
            'name': name,
            'params': params,
            'metrics': metrics,
            'data_period': data_period,
            'notes': notes,
        }
        self.experiments.append(record)
        self._save()
        return record['id']

    def list_all(self) -> pd.DataFrame:
        if not self.experiments:
            return pd.DataFrame()
        # json_normalize flattens metrics.sharpe etc. into columns for sorting
        return pd.json_normalize(self.experiments)

    def best_by(self, metric: str, n: int = 5) -> pd.DataFrame:
        df = self.list_all()
        if df.empty:
            return df
        metric_col = f'metrics.{metric}'
        if metric_col in df.columns:
            return df.sort_values(metric_col, ascending=False).head(n)
        return df.head(n)

    def get(self, experiment_id: int) -> Optional[Dict]:
        for exp in self.experiments:
            if exp['id'] == experiment_id:
                return exp
        return None

    def delete(self, experiment_id: int) -> bool:
        for i, exp in enumerate(self.experiments):
            if exp['id'] == experiment_id:
                del self.experiments[i]
                self._save()
                return True
        return False
