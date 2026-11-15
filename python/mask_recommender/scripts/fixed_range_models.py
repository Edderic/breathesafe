"""Fixed physical bounds; no data-derived min/max, z-score or silent clipping."""
import json
from pathlib import Path

import numpy as np

from mask_recommender.scripts.compare_direct_measurements import FaceMaskClassifier

CONFIG_PATH = Path(__file__).with_name('fixed_range_scaling.json')
CONFIG = json.loads(CONFIG_PATH.read_text())


class FixedPhysicalScaler:
    def __init__(self, columns, ranges=None):
        self.columns = list(columns)
        ranges = CONFIG['ranges'] if ranges is None else ranges
        self.lower = np.array([ranges[k][0] for k in self.columns], dtype=float)
        self.width = np.array([ranges[k][1]-ranges[k][0] for k in self.columns], dtype=float)
        if np.any(self.width <= 0):
            raise ValueError('Fixed ranges must have positive width')

    def fit(self, values):
        self.transform(values)
        return self

    def transform(self, values):
        values = np.asarray(values, dtype=float)
        if values.ndim != 2 or values.shape[1] != len(self.columns) or not np.isfinite(values).all():
            raise ValueError('Invalid fixed-range measurements')
        result = (values-self.lower)/self.width
        if np.any(result < -1e-10) or np.any(result > 1+1e-10):
            bad = np.any((result < -1e-10) | (result > 1+1e-10), axis=0)
            raise ValueError('Measurements outside prespecified ranges: '+', '.join(np.array(self.columns)[bad]))
        return result

    def fit_transform(self, values):
        return self.fit(values).transform(values)


def bounded_pc_scores(pca, scaled):
    # A linear projection reaches its cube minimum at coordinates whose loading
    # is negative, and its maximum at positive-loading coordinates. Subtracting
    # the PCA mean cancels between score and lower bound.
    component_minimum = np.minimum(pca.components_, 0).sum(axis=1)
    component_width = np.abs(pca.components_).sum(axis=1)
    return (np.asarray(scaled)@pca.components_.T-component_minimum)/component_width


class FixedRangeClassifier(FaceMaskClassifier):
    def __init__(self, arm, components=3):
        super().__init__(arm)
        self.face_scaler = FixedPhysicalScaler(self.columns)
        self.perimeter_scaler = FixedPhysicalScaler(['mask_perimeter_mm'])
        if self.pca is not None:
            self.pca.set_params(n_components=components)

    def geometry(self, frame, people):
        values = people.set_index('user_id').loc[frame.user_id, self.columns].to_numpy(dtype=float)
        scaled = self.face_scaler.transform(values)
        return bounded_pc_scores(self.pca, scaled) if self.pca is not None else scaled
