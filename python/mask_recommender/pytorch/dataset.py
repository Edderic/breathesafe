from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from .features import split_feature_types


@dataclass
class StandardizationStats:
    mean: np.ndarray
    std: np.ndarray


class TabularFitDataset(Dataset):
    """
    Simple tabular dataset wrapper.

    Expects a DataFrame with:
      - features as columns
      - target column `target` (int class index: 0,1,2)
    """

    def __init__(
        self,
        df: pd.DataFrame,
        feature_names: List[str],
        target_col: str = "target",
        standardize_numeric: bool = True,
        stats: Optional[StandardizationStats] = None,
    ) -> None:
        self.df = df.copy()
        self.feature_names = list(feature_names)
        self.target_col = target_col
        self.standardize_numeric = standardize_numeric

        # Fill missing values: numeric -> 0, binary -> 0
        config = split_feature_types(self.feature_names)
        for c in config.numerical + config.binary:
            if c not in self.df.columns:
                # if a column is absent, create it with zeros
                self.df[c] = 0
        self.df[config.numerical] = self.df[config.numerical].fillna(0)
        self.df[config.binary] = self.df[config.binary].fillna(0).clip(0, 1)

        # compute or use provided stats for standardization
        self.numeric_idx = np.array([
            i for i, f in enumerate(self.feature_names) if f in config.numerical
        ], dtype=np.int64)
        if standardize_numeric:
            if stats is None:
                mean = self.df[config.numerical].to_numpy(dtype=np.float32).mean(axis=0)
                std = self.df[config.numerical].to_numpy(dtype=np.float32).std(axis=0)
                std = np.where(std == 0, 1.0, std)
                self.stats = StandardizationStats(mean=mean, std=std)
            else:
                self.stats = stats
        else:
            self.stats = None

        # build tensors
        X = self.df[self.feature_names].to_numpy(dtype=np.float32)
        if self.stats is not None and self.numeric_idx.size > 0:
            X[:, self.numeric_idx] = (X[:, self.numeric_idx] - self.stats.mean) / self.stats.std
        self.X = torch.from_numpy(X)

        if target_col in self.df.columns:
            self.y = torch.from_numpy(self.df[target_col].to_numpy(dtype=np.int64))
        else:
            self.y = None

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        if self.y is None:
            return self.X[idx], None
        return self.X[idx], self.y[idx]

    def get_stats(self) -> Optional[StandardizationStats]:
        return self.stats
