from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import torch
import torch.nn as nn


@dataclass
class MLPConfig:
    input_dim: int
    hidden_dim: int = 64
    depth: int = 2
    dropout: float = 0.0
    num_classes: int = 3  # 0=too small, 1=ok, 2=too big


class FitClassifier(nn.Module):
    def __init__(self, config: MLPConfig) -> None:
        super().__init__()
        layers = []
        dim = config.input_dim
        for _ in range(max(0, config.depth)):
            layers.append(nn.Linear(dim, config.hidden_dim))
            layers.append(nn.ReLU())
            if config.dropout > 0:
                layers.append(nn.Dropout(config.dropout))
            dim = config.hidden_dim
        layers.append(nn.Linear(dim, config.num_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
