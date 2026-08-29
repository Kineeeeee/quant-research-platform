import json
import os
from typing import Dict, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ExperimentConfig:
    """
    One experiment as data, not hardcoded script args - so runs are
    reproducible and easy to sweep. Load from a dict or a JSON file.
    """
    strategy: str = ""
    params: Dict = field(default_factory=dict)
    data: Dict = field(default_factory=dict)
    backtest: Dict = field(default_factory=dict)
    notes: str = ""

    @classmethod
    def from_dict(cls, d: Dict) -> 'ExperimentConfig':
        return cls(
            strategy=d.get('strategy', ''),
            params=d.get('params', {}),
            data=d.get('data', {}),
            backtest=d.get('backtest', {}),
            notes=d.get('notes', ''),
        )

    @classmethod
    def from_file(cls, filepath: str) -> 'ExperimentConfig':
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Config file {filepath} not found.")
        with open(filepath, 'r') as f:
            return cls.from_dict(json.load(f))

    def save(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def to_dict(self) -> Dict:
        return asdict(self)
