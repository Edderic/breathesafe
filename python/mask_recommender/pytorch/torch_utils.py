import os
from typing import Any

import torch


def init_torch() -> Any:
    try:
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
    except Exception:
        pass
    return torch
